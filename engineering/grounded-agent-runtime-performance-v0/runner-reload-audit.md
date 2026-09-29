# Runner reload audit

The promoted action path inherits fixed action options from experiments/grounded_autonomous_agent_v0/protocol.py and experiments/grounded_autonomous_agent_v0_2/protocol.py: num_ctx 2048, with no per-decision GPU, low_vram, batch, or thread override. Seeds change by decision and num_predict is 48, but the runner-level context remains fixed. The controlled-pairing worker uses that same action interface. Its paired I/S calls occur in sequence, with one shared call at a matched inactive boundary.

The separate grounded_self_diagnosis_v0/protocol.py sets num_ctx 8192 and num_predict 1024. Interleaving that retrospective role with the 2048-token action role on this Ollama 0.1.16 service can replace the runner. Historical model-level parameters say num_ctx 4096; explicit action/review requests override that default. Older model-map and repair sources inspected request 2048. No source inspected requests num_gpu, low_vram, main_gpu, or a runner batch override. The action-model reproducibility audit intentionally used keep_alive:0 in a control; it is not the ordinary campaign behavior.

Read-only aggregate of preserved private timing metadata, without copying request or response bodies:

| Completed campaign | Unique physical attempts | Loads over 1 s | Maximum load | Median warm load |
| --- | ---: | ---: | ---: | ---: |
| Controlled stochastic pairing | 58 | 1 | 35.488 s | 0.000399 s |
| Eligibility completion | 42 | 1 | 38.917 s | about 0.0005 s |

Thus repeated full reloads were not observed within those campaigns. The existing action-model audit separately recorded 20 deliberately fresh-runner controls with distinct PIDs and loads above five seconds. This engineering benchmark observed a cold first call of 37.701 s. The separate 8192-token review probe changed the runner from PID 2902435 (2048 context, 20 GPU layers) to PID 2909789 (8192 context, 20 GPU layers); the server log recorded 6.201 s runner startup. The review request then timed out after 900 s without phase metadata. The restoration call changed back to PID 2925004 (2048 context, 21 GPU layers), with 5.117 s load_duration and 9.711 s total wall. The server binary, model artifact and historical source remained unchanged.

Scheduling same-context requests together and keeping a runner warm can avoid the measured intermittent load cost without changing model identity, prompt bytes, or decision logic. This is a candidate operational change only; no historical script or server default was changed. For future work, preserve exact request payloads and separately verify that changed scheduling does not alter stochastic output distributions or provenance. Do not normalize an 8192-token review to 2048: that would truncate or otherwise change the model input and cannot be treated as a transparent speed optimization.
