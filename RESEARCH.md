# Research and scope — 16 October 2026

## Brief

User: Outdoor-track analysts reviewing apparent stops and capture gaps before summarizing a GPX activity.

Pain: A long interval between nearby points can be a sampling gap rather than a recorded stop, and slow GPS drift or jumps can distort moving/stopped summaries.

Smallest useful capability: Read actual GPX1.1 track segments and emit fixed-anchor dwell windows, separate gap/speed-jump evidence and raw versus accepted pair totals.

Acceptance: Synthetic three-point stationary run yields120 seconds, then ends before a moving point. Segments, gaps and speed jumps cannot manufacture a joined stop. Slow drift, dateline crossing, prefixes, timezone equivalence and malformed XML/times/coordinates are tested.

Demand is inferred from the workflow and adjacent public discussions, not a verified request for this project. Discovery: precise GitHub topics, this runnable example and the chronological profile index; no unsolicited outreach or activity manipulation.

## Comparables

Live GitHub repository search, sort **Most stars**, query `GPX analyzer in:description`. Highest-star relevant comparable found within this search scope: **tumic0/GPXSee**. Search coverage is limited; this is not an exhaustive worldwide ranking. Broad queries returned unrelated products and were filtered by the actual user workflow.

| Repository | Stars observed | Last push observed (UTC) | Archived | API license classification |
| --- | ---: | --- | --- | --- |
| [tumic0/GPXSee](https://github.com/tumic0/GPXSee) | 1251 | 2026-10-15T15:58:53Z | False | GPL-3.0 |
| [gpxstudio/gpx.studio](https://github.com/gpxstudio/gpx.studio) | 1240 | 2026-10-14T06:17:58Z | False | MIT |
| [tkrajina/gpxpy](https://github.com/tkrajina/gpxpy) | 1108 | 2026-09-26T11:50:36Z | False | Apache-2.0 |

Exact observation times, README blob identities and up to five issue/PR references per comparable are in [research provenance](RESEARCH_PROVENANCE.json). NOASSERTION means the API did not classify the license; it is not permission to reuse. Stars are discovery evidence, not a measure of quality, performance or reliability.

GPXSee is a broad GPS viewer/analyzer, gpx.studio edits GPX in the browser, and gpxpy already offers moving/stopped data methods. Current gpxpy issue/PR discussions include zero stopped-speed thresholds, stationary intervals and prefixed namespaces; our tests explicitly cover these edges without claiming a new feature competitors lack. A gpx.studio issue asks for summary data, but it is adjacent interest rather than a verified request for our tool.

Workflow alternatives: GPXSee for desktop inspection, gpx.studio for interactive editing and gpxpy for Python GPX analysis. Broad GPX search also returned hardware firmware, galleries and activity homepages; those were outside the selected offline dwell-report workflow.

Our install is a small Python wheel and two or fewer input steps, with a synthetic example and explicit failure states. Competitors offer broader interfaces, integrations, formats, documentation and support communities; their current READMEs/code and issue discussions were inspected, but their installations, reliability, support response and time to first useful result were not measured here. Our successful example establishes only our stated behavior. Licensing was recorded, not used as a proxy for capability.

Portfolio distinction: geojson-delivery-contract validates geospatial delivery geometry and subtitle-timing-audit handles media timing. This parses GPX track segmentation and spatial/time dwell evidence.

## Claims and reuse

No technical performance benchmark was conducted. There is no speed, memory, reliability or feature-absence superiority claim. Standard algorithms/formats are not inventions of this project. Source references were read for semantics and workflow comparison; implementation, prose and synthetic fixtures were written for this project. No third-party code, font assets or sample user data is bundled. No competitor logos/branding are reused.
