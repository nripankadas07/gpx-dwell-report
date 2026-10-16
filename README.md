# gpx-dwell-report

Read actual GPX1.1 track segments and emit fixed-anchor dwell windows, separate gap/speed-jump evidence and raw versus accepted pair totals.

For: Outdoor-track analysts reviewing apparent stops and capture gaps before summarizing a GPX activity. A long interval between nearby points can be a sampling gap rather than a recorded stop, and slow GPS drift or jumps can distort moving/stopped summaries.

## Quickstart

Python 3.10 or newer. No runtime packages or network requests. The initial wheel build needs setuptools from the normal Python package registry.

```sh
git clone https://github.com/nripankadas07/gpx-dwell-report.git
cd gpx-dwell-report
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/gpx-dwell-report example.gpx
```

The synthetic equatorial example contains one120-second anchored dwell window and no gap/speed findings. It uses invented coordinates, not a personal track.

Windows: use `.venv\Scripts\python.exe` and `.venv\Scripts\gpx-dwell-report.exe` instead. Windows is documented but has not been executed in this release's Linux CI.

## Input and result contract

UTF-8 GPX1.1 namespace/version only, <=2 MiB, <=100 tracks, <=1000 segments and <=20000 track points. Match namespace plus element name; extension/route points are not tracks. Every track point needs lat/lon and exactly one timezone-aware ISO8601 time (<=6 fraction digits, offset<=14h); timestamps strictly increase within a segment. Spherical haversine distances use radius6371008.8m. Dwell is a greedy contiguous fixed-anchor run inside radius_m, meeting dwell_s, with each intervening gap and speed within max_gap_s/max_speed_mps. Threshold equality is accepted; zero radius is allowed. Segment/gap/jump boundaries never bridge windows. Defaults:25m,120s,300s,80m/s. Radius<=1000000m, dwell/gap<=30days, speed<=100000m/s.

Output is JSON on stdout. Exit 0 means complete/no findings; exit 1 means a valid report with missing coverage, prices, capacity, or capture findings, where applicable. SQLite extraction has no exit-1 state. Exit 2 means invalid input or an I/O failure, with an error on stderr and no partial report. `--help` describes command options. Inputs stay local; review output before sharing it.

## Limits

An anchored heuristic over captured points, not proof of physical stops, true moving time, GPS accuracy or navigational safety. No interpolation, geodesic ellipsoid, map matching, elevation, GPX1.0/FIT/TCX importer or editing. Rejected jumps are reported, not corrected or deleted. Output includes supplied coordinates, so review locally before sharing. No coordinates or files are sent to a service.

## Verify

```sh
python3 -m unittest -v test_behavior
python3 -m compileall -q .
python3 -m pip wheel --no-deps --wheel-dir dist .
python3 -m venv /tmp/gpx-dwell-report-check
/tmp/gpx-dwell-report-check/bin/python -m pip install --no-deps dist/*.whl
python3 verify_installed.py /tmp/gpx-dwell-report-check/bin/python
```

The installed-command check runs outside the checkout. See [validation](VALIDATION.md), [research and tradeoffs](RESEARCH.md), [contributing](CONTRIBUTING.md), [support](SUPPORT.md) and [security](SECURITY.md).

Original implementation and synthetic fixtures, developed with AI assistance and reviewed through executable checks. MIT license. No customer/adoption claims, copied competitor implementation, or performance-superiority claim.
