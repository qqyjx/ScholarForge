---
type: llm
name: direct-rewrite
weight: 2
---

PASS if the answer directly gives one rewritten sentence of at most 15 words that keeps the meaning (process reward, multi-step reasoning, policy optimization, experiments on several benchmarks). One sentence explaining the cut is allowed.

FAIL if it suggests re-planning the project, adding experiments, starting a review, asks to see the whole paper first, or outputs a multi-paragraph process description instead of the rewritten sentence.
