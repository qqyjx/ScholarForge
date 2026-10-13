# Common rejection patterns

These ten patterns recur in reviews of rejected ML papers. Where both human referees and an automated AI review are present, the automated review tends to catch mechanically checkable problems (missed nearest neighbors, contradictory numbers, theorems that clash with remarks, mismatched statistical tests). Human referees focus on three things: the system sold is not the system measured, theorem assumptions are not measured, and the prose reads as LLM-written.

| # | Pattern | Example shape |
|---|---|---|
| 1 | **Title and abstract sell the whole system; experiments measure a subset or a proxy** | Three signals claimed, one sampling frequency measured; theorem for one parameter value, all runs at another; "semantic" gains that a capacity-matched control would reproduce; one backbone only |
| 2 | **Theorem assumptions are the properties the method should produce, and none is measured** | Bounded error, decorrelation, or consistency assumed rather than measured |
| 3 | **No isolating control for the novel component** (replace it, keep everything else) | A learned module never compared with a detector, attention, or random choice |
| 4 | **Statistical mismatch** | Independent tests on paired data (same prompt or image); no training-seed variance; estimator with too little resolution; single values with no error bars |
| 5 | **Cross-protocol baselines** | Published numbers next to self-run numbers; baselines on a lossy channel while the method uses a persistent medium |
| 6 | **Prose flagged as LLM-like** | See the six tells in P2 |
| 7 | **Missing nearest neighbors** | Automated reviews typically list 2-5 per paper |
| 8 | **Self-contradicting numbers, or a headline refuted by the paper's own table** | A statistic above its theoretical bound; an impossible percentage for the number of runs; "consistent gains" with one worse cell |
| 9 | **Planned experiments written into the paper** | "Queued for the camera-ready"; an RQ describing an ablation that has not run |
| 10 | **Terms used before definition, objects used before introduction, main algorithm in the appendix** | One word with two meanings |

## Countermeasures

These are built into the stage files:

- P0: scope sold equals scope measured; a replace-it control arm for every novel component.
- P1: assumption measurement table; paired tests; identical protocols; no planned experiments in the paper.
- P2: the six LLM-tell scan; define terms first; check headline sentences against tables.
- P4: rehearse the automated review before submitting (`scripts/ai_review_preflight.py` plus simulated referees and a nearest-neighbor persona). Simulated review-form referees and an adversarial self-review cover patterns 3, 4, 7, and 8; the preflight script adds explicit checks for 1, 2, 6, and 9.
