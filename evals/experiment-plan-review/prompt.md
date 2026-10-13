---
max_turns: 8
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

Review my experiment plan against the /paper-lifecycle experiment standards. Target: ICLR main track.

- Method: add a "process reward + entropy gate" module on top of GRPO (two mechanisms)
- Main table: our method vs GRPO / PPO / DPO on MATH-500 and AIME24
- One seed per cell, final checkpoint
- No ablations; we will add them if referees ask
- Criterion: the claim holds if we beat the strongest baseline in the main table

Is this enough to submit? If not, list what is missing by priority.
