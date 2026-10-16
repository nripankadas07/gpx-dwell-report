import unittest
from gpx_dwell_report import analyze,parse,distance,timestamp


def gpx(segments,prefix=False):
    p='g:' if prefix else ''
    attr='xmlns:g' if prefix else 'xmlns'
    body=''.join('<'+p+'trkseg>'+''.join(f'<{p}trkpt lat="{lat}" lon="{lon}"><{p}time>{t}</{p}time></{p}trkpt>' for lat,lon,t in points)+'</'+p+'trkseg>' for points in segments)
    return f'<{p}gpx {attr}="http://www.topografix.com/GPX/1/1" version="1.1"><{p}trk>{body}</{p}trk></{p}gpx>'


def point(t,lon=0,lat=0):return (lat,lon,f'2026-01-01T00:{t//60:02d}:{t%60:02d}Z')


class DwellTests(unittest.TestCase):
    def test_stationary_window(self):
        r=analyze(gpx([[point(0),point(60),point(120),point(180,.001)]]))
        self.assertEqual(r['dwell_seconds'],120)
        self.assertEqual((r['dwell_windows'][0]['first_point'],r['dwell_windows'][0]['last_point']),(0,2))

    def test_no_bridge_between_segments(self):
        r=analyze(gpx([[point(0),point(60)],[point(120),point(180)]]))
        self.assertEqual(r['dwell_windows'],[])

    def test_no_bridge_across_sampling_gap(self):
        r=analyze(gpx([[point(0),point(60),point(600),point(660)]]),max_gap_s=300)
        self.assertEqual(r['dwell_windows'],[])
        self.assertEqual(r['findings'][0]['reasons'],['sampling_gap'])
        self.assertEqual(r['segments'][0]['accepted_pair_seconds'],120)

    def test_speed_jump_breaks_window_and_is_not_removed_silently(self):
        r=analyze(gpx([[point(0),point(60),point(61,1),point(181,1)]]))
        self.assertIn('speed_jump',r['findings'][0]['reasons'])
        self.assertEqual(r['dwell_seconds'],120)

    def test_fixed_anchor_rejects_slow_drift(self):
        r=analyze(gpx([[point(0),point(60,.00015),point(120,.0003),point(180,.00045)]]))
        self.assertEqual(r['dwell_windows'],[])

    def test_zero_radius_is_supported(self):
        r=analyze(gpx([[point(0),point(120)]]),radius_m=0)
        self.assertEqual(r['dwell_seconds'],120)

    def test_threshold_is_inclusive(self):
        r=analyze(gpx([[point(0),point(120)]]),dwell_s=120,max_gap_s=120)
        self.assertEqual(r['dwell_seconds'],120)
        self.assertEqual(r['findings'],[])

    def test_prefixed_namespace(self):
        r=analyze(gpx([[point(0),point(120)]],True))
        self.assertEqual(r['dwell_seconds'],120)

    def test_timezone_equivalence(self):
        self.assertEqual(timestamp('2026-01-01T04:00:00+04:00'),timestamp('2026-01-01T00:00:00Z'))

    def test_antimeridian_uses_short_arc(self):
        self.assertAlmostEqual(distance((0,179.999),(0,-179.999)),222.39016,places=3)

    def test_missing_duplicate_and_descending_times(self):
        for pts in [[point(0),point(0)],[point(60),point(0)]]:
            with self.subTest(pts=pts),self.assertRaises(ValueError):parse(gpx([pts]))
        s=gpx([[point(0)]]).replace('<time>2026-01-01T00:00:00Z</time>','')
        with self.assertRaises(ValueError):parse(s)
        s=gpx([[point(0)]]).replace('</time>','</time><time>2026-01-01T00:01:00Z</time>')
        with self.assertRaises(ValueError):parse(s)

    def test_timezone_required_and_nonfinite_coordinates_refused(self):
        for t in ['2026-01-01T00:00:00','2026-01-01T00:00:60Z','2026-01-01T00:00:00+15:00']:
            with self.subTest(t=t),self.assertRaises(ValueError):timestamp(t)
        for lat,lon in [('NaN',0),(91,0),(0,181),(0,'inf')]:
            with self.subTest(lat=lat,lon=lon),self.assertRaises(ValueError):parse(gpx([[(lat,lon,'2026-01-01T00:00:00Z')]]))

    def test_dtd_and_entity_refused(self):
        s='<!DOCTYPE gpx [<!ENTITY x "expansion">]>'+gpx([[point(0)]])
        with self.assertRaisesRegex(ValueError,'DTD'):parse(s)

    def test_foreign_namespace_does_not_impersonate_gpx(self):
        with self.assertRaises(ValueError):parse(gpx([[point(0)]]).replace('GPX/1/1','other/1/1'))

    def test_empty_segments_and_one_point(self):
        r=analyze(gpx([[],[point(0)]]))
        self.assertEqual(r['dwell_windows'],[])
        self.assertEqual(r['segments'][0]['span_seconds'],0)

    def test_parameter_bounds(self):
        for k,v in [('radius_m',-1),('dwell_s',0),('max_gap_s',0),('max_speed_mps',float('nan'))]:
            with self.subTest(k=k),self.assertRaises(ValueError):analyze(gpx([[point(0)]]),**{k:v})

    def test_byte_limit_and_wrong_encoding(self):
        with self.assertRaises(ValueError):parse(' '*(2*1024*1024+1))
        with self.assertRaises(ValueError):parse('<?xml version="1.0" encoding="UTF-16"?>'+gpx([[point(0)]]))

    def test_tracks_are_not_routes_or_extensions(self):
        s=gpx([[point(0)]]).replace('<trk>','<extensions><trk>').replace('</trk>','</trk></extensions>')
        with self.assertRaises(ValueError):parse(s)


if __name__=='__main__':unittest.main()
