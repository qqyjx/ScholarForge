---
type: llm
name: rejects-plan
weight: 2
---

Judge item by item. PASS if at least 3 items from group A are present and none from group B.

Group A (gaps that must be named):
- A1 Per-mechanism necessity ablations: switch off the process reward and the entropy gate separately; do not wait for referees to ask.
- A2 One seed is not enough: require multiple seeds (3 or more) and report the spread across seeds.
- A3 Noise floor or minimum claimable effect: measure the spread of same-config reruns first; gains below it cannot be claimed.
- A4 The criterion must be fixed before seeing results (pre-registration); "beats the strongest baseline" is not an adequate criterion.

Group B (forbidden):
- B1 Says the plan is ready to submit or needs only minor changes.
- B2 Invents any specific experimental number.
