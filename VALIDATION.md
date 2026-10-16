# Validation

Acceptance contract: Synthetic three-point stationary run yields120 seconds, then ends before a moving point. Segments, gaps and speed jumps cannot manufacture a joined stop. Slow drift, dateline crossing, prefixes, timezone equivalence and malformed XML/times/coordinates are tested.

The behavior suite has 18 test methods; this includes meaningful malformed-input cases. CI executes unit tests, Python compilation, wheel build and a new-environment installed-console-command check on Linux/Python 3.10, 3.12 and 3.14. A configured workflow is not proof it passed: inspect this repository's current Actions run before making a health claim.

Preparation: all behavior tests passed on Python 3.12.14. Clean wheel/CLI evidence is recorded in `PREPARATION.json` after execution. Future security advisories, all possible inputs and Windows/macOS behavior are not certified by these checks. No performance benchmark or production-use evidence is claimed.
