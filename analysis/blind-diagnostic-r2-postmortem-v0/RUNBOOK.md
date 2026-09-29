# Running the frozen postmortem

`python analysis/blind-diagnostic-r2-postmortem-v0/analyze.py --output-dir NEW_DIRECTORY`

The output directory must not already exist. The analyzer checks the committed codebook and exact public input hashes, uses the original strict parser and full frozen schema, copies all scorer credits, and emits deterministic files. It never invokes scientific scoring functions, a model, a server, Horus, or private evidence. The codebook defines how absent fields, alternatives, overlapping codes, and count denominators are handled.

The first generated artifact set is stored in `deterministic/`. A second invocation into a new temporary directory must reproduce every artifact byte. Commit the artifacts and replay proof before inspecting the five selected examples for qualitative illustration.

`python analysis/blind-diagnostic-r2-postmortem-v0/test_analysis.py` runs synthetic mechanical edge cases only.
