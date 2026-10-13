---
type: llm
name: answer-correct
---

PASS if both hold:
1. Correct content: GRPO computes a group-relative advantage from several samples for the same prompt (normalized by the group mean and standard deviation), so it does not need PPO's value (critic) network.
2. Form: a direct short explanation (at most about 120 words, three points are fine), with no paper-workflow stages and no request for more information.

Do not FAIL only because the sentence count is not exactly three.
