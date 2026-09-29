# Prompt-size scaling on the historical runtime

All six scaling probes used the same model, num_ctx 2048, num_predict 8, JSON mode and sampling options, with no world or Memory access. The input is synthetic repeated neutral text; the measured token count includes Ollama's template overhead. All six calls were warm, with load below 0.001 s.

| Frozen synthetic target | Actual input tokens | Prompt evaluation | Effective prompt tokens/s | Output tokens |
| ---: | ---: | ---: | ---: | ---: |
| about 50 | 75 | 3.962 s | 18.9 | 1 |
| about 100 | 125 | 5.318 s | 23.5 | 8 |
| about 250 | 275 | 9.673 s | 28.4 | 1 |
| about 500 | 525 | 17.020 s | 30.8 | 1 |
| about 1000 | 1025 | 31.676 s | 32.4 | 1 |
| about 1900 | 1925 | 58.704 s | 32.8 | 1 |

Prompt evaluation rose monotonically by 54.74 s from the smallest to largest probe. Output was intentionally tiny; one-token completion timings are too small to yield a meaningful generation-rate estimate. These repeated-word probes can benefit from repeated prefix/cache behavior or Mixtral expert locality, so their throughput must not be extrapolated directly to diverse research prompts.

Read-only archived timing metadata put the real action workload in the same size range: the controlled-pairing campaign had 58 unique attempts with median 559.5 input tokens and 25.06 s prompt evaluation; the eligibility campaign had 42 attempts with median 564 tokens and 32.08 s prompt evaluation. No private prompt or output was copied.

An additional tiny probe measured exactly 30 API-reported input tokens, one output token, 1.869 s prompt evaluation and 1.920 s warm wall time. The diverse public-safe benchmark shapes were slower: 55 tokens took 3.524 s warm, 107 took 6.446 s, 559 representative action tokens took 31.818 s, and a bounded 1554-token retrospective shape took 88.820 s. For the 559-token action shape, 31.818 of 32.800 wall seconds were prompt evaluation (97.0%); eight output tokens took 0.974 s. The bounded retrospective shape spent 98.8% of wall time in prompt evaluation. This establishes prompt processing as the largest measured warm-call component, while the separate 30-decision review probe had a 6321-token rendered input by local tokenization and timed out after 900 s. It returned no Ollama prompt_eval_count or phase durations, so the long-context latency cannot be split into prefill and generation. This mirrors the transport failure mode of the preserved INVALID historical self-diagnosis study without changing its classification.

No prompt was scored for action quality. The compact candidate in compact-model-view.md is a proposed future interface only.
