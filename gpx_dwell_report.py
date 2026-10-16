"""Explain anchored dwell windows without bridging GPX segments, gaps or speed jumps."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS = "{http://www.topografix.com/GPX/1/1}"
MAX_BYTES = 2 * 1024 * 1024
TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})")


def timestamp(text):
    if not isinstance(text, str) or not TIME.fullmatch(text):
        raise ValueError("point times need explicit ISO8601 timezone and <=6 fractional digits")
    result = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    if abs(result.utcoffset().total_seconds()) > 14 * 3600:
        raise ValueError("timezone offset exceeds 14 hours")
    return result.astimezone(dt.timezone.utc)


def finite(value, low, high, label):
    if isinstance(value, bool):
        raise ValueError(label + " must be numeric")
    try:
        x = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(label + " must be finite numeric") from None
    if not math.isfinite(x) or not low <= x <= high:
        raise ValueError(label + " out of range")
    return x


def distance(a, b):
    lat1, lat2 = math.radians(a[0]), math.radians(b[0])
    dlat = lat2 - lat1
    dlon = math.radians(b[1] - a[1])
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371008.8 * 2 * math.asin(math.sqrt(min(1.0, max(0.0, h))))


def parse(text):
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("GPX input exceeds 2 MiB")
    if re.search(r"<!\s*(?:DOCTYPE|ENTITY)", text, re.I):
        raise ValueError("DTD/entity declarations are unsupported")
    enc = re.search(r"<\?xml[^>]*encoding\s*=\s*['\"]([^'\"]+)", text, re.I)
    if enc and enc[1].lower() not in ("utf-8", "utf8"):
        raise ValueError("only UTF-8 GPX is supported")
    root = ET.fromstring(text)
    if root.tag != NS + "gpx" or root.get("version") != "1.1":
        raise ValueError("expected GPX1.1 namespace and version")
    tracks = root.findall(NS + "trk")
    if len(tracks) > 100:
        raise ValueError("at most 100 tracks")
    result = []
    total = 0
    for ti, track in enumerate(tracks):
        for si, segment in enumerate(track.findall(NS + "trkseg")):
            points = []
            if len(result) >= 1000:
                raise ValueError("at most 1000 track segments")
            for point in segment.findall(NS + "trkpt"):
                total += 1
                if total > 20000:
                    raise ValueError("at most 20000 track points")
                lat = finite(point.get("lat"), -90, 90, "latitude")
                lon = finite(point.get("lon"), -180, 180, "longitude")
                times = point.findall(NS + "time")
                if len(times) != 1:
                    raise ValueError("each track point requires exactly one GPX time")
                time = timestamp(times[0].text)
                if points and time <= points[-1][2]:
                    raise ValueError("times must strictly increase within each segment")
                points.append((lat, lon, time))
            result.append((ti, si, points))
    if not total:
        raise ValueError("no GPX track points found; routes/waypoints are not track segments")
    return result


def analyze(text, radius_m=25, dwell_s=120, max_gap_s=300, max_speed_mps=80):
    radius = finite(radius_m, 0, 1000000, "radius_m")
    dwell = finite(dwell_s, 0.000001, 86400 * 30, "dwell_s")
    gap = finite(max_gap_s, 0.000001, 86400 * 30, "max_gap_s")
    speed = finite(max_speed_mps, 0.000001, 100000, "max_speed_mps")
    segments = parse(text)
    reports, stops, findings = [], [], []
    for ti, si, points in segments:
        accepted_seconds = raw_distance = accepted_distance = 0.0
        anchor = 0

        def emit(end):
            if end <= anchor:
                return
            duration = (points[end][2] - points[anchor][2]).total_seconds()
            if duration >= dwell:
                stops.append({"track": ti, "segment": si, "first_point": anchor, "last_point": end,
                              "start_utc": points[anchor][2].isoformat(), "end_utc": points[end][2].isoformat(),
                              "duration_seconds": duration, "anchor_lat": points[anchor][0], "anchor_lon": points[anchor][1],
                              "maximum_anchor_distance_m": round(max(distance(points[anchor], p) for p in points[anchor:end + 1]), 6)})

        for i in range(1, len(points)):
            seconds = (points[i][2] - points[i - 1][2]).total_seconds()
            meters = distance(points[i - 1], points[i])
            raw_distance += meters
            reasons = []
            if seconds > gap:
                reasons.append("sampling_gap")
            if meters / seconds > speed:
                reasons.append("speed_jump")
            if reasons:
                emit(i - 1)
                findings.append({"track": ti, "segment": si, "from_point": i - 1, "to_point": i,
                                 "seconds": seconds, "distance_m": round(meters, 6), "reasons": reasons})
                anchor = i
                continue
            accepted_seconds += seconds
            accepted_distance += meters
            if distance(points[anchor], points[i]) > radius:
                emit(i - 1)
                anchor = i
        emit(len(points) - 1)
        reports.append({"track": ti, "segment": si, "points": len(points),
                        "span_seconds": (points[-1][2] - points[0][2]).total_seconds() if points else 0,
                        "accepted_pair_seconds": accepted_seconds, "raw_pair_distance_m": round(raw_distance, 6),
                        "accepted_pair_distance_m": round(accepted_distance, 6)})
    return {"parameters": {"radius_m": radius, "dwell_s": dwell, "max_gap_s": gap, "max_speed_mps": speed},
            "segments": reports, "dwell_windows": stops, "dwell_seconds": sum(s["duration_seconds"] for s in stops),
            "findings": findings,
            "scope": "Greedy fixed-anchor windows over observed points; no interpolation, map matching or proof of physical stops. Coordinates remain in this local output."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", help="UTF-8 GPX1.1 file")
    p.add_argument("--radius-m", type=float, default=25)
    p.add_argument("--dwell-s", type=float, default=120)
    p.add_argument("--max-gap-s", type=float, default=300)
    p.add_argument("--max-speed-mps", type=float, default=80)
    a = p.parse_args()
    try:
        with Path(a.input).open("rb") as f:
            raw = f.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("GPX file exceeds 2 MiB")
        report = analyze(raw.decode("utf-8-sig"), a.radius_m, a.dwell_s, a.max_gap_s, a.max_speed_mps)
        print(json.dumps(report, sort_keys=True, indent=2))
        return 1 if report["findings"] else 0
    except (ValueError, OSError, UnicodeError, ET.ParseError, OverflowError, RecursionError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
