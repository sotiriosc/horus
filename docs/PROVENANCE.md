# Source, data and tool provenance

Project-authored source carries the repository's CERN-OHL-S-2.0 license; existing attribution notices are retained. This does not change licenses of separately installed tools or data.

The digit demonstration loads `sklearn.datasets.load_digits` from the user's scikit-learn installation. It does not redistribute that dataset in this repository. Its description and attribution can be inspected through `load_digits().DESCR`. Generated weights, test images and figures remain run artifacts.

The four retained tile fixtures are synthetic numerical vectors associated with the project's existing arithmetic tests, not language data, personal records, or model weights. Their role and hashes are listed in [EVIDENCE.md](EVIDENCE.md).

No LLM runner, bundled language corpus, generated prompt/output collection, model weight or tokenizer cache is redistributed. Prior LLM measurements used a fallback corpus after dataset-cache access failed; those runs must not be described as WikiText results. Excluding that experiment family avoids implying a validated redistribution/provenance boundary or standalone reproduction that this candidate does not provide.

Sky130 liberty files, Yosys/ABC and Icarus are independently installed. Their licensing and attribution remain with their distributions. Citation of Dream-RSI links to the authors' paper; no paper text or third-party implementation is vendored.

Fresh runs identify the executed files by content hashes. No earlier repository commit identifier is treated as proof of the candidate's source state.
