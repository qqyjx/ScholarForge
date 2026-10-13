# EXPERIMENT PROGRAM - <codename>

> Criteria: `references/top-venue-bar.md` section 2. Do not open the extension matrix until the core matrix survives. Every cell has a budget and a kill order.

## Core matrix (the headline lives or dies here)

| Dimension | Plan | Floor |
|---|---|---|
| Model families x scales | | 2+ families x 2+ scales, or 3+ scales in one family |
| Evaluation settings | | 3+, including 1+ mainstream benchmark |
| Training seeds per cell | | 3+ |
| Noise floor | same-config reruns x N | its own row |
| Baselines | | 6+, 2+ from the last 12 months, including the strongest trivial baseline |
| Headline criterion | effect >= 2x noise floor, paired test, CI | otherwise report null |

Budget: __ GPU-h per cell x __ cells = __ GPU-h. One unit measured at full cost first: __ h (date measured).

## Extension matrix (each item -> one figure; cut in kill order)

| Kill order | Item | Plan | Figure | Budget | Status |
|---|---|---|---|---|---|
| 1 (cut last) | Leave-one-out ablation | | F5 | | |
| 2 | Mechanism analysis | | F6 | | |
| 3 | Scaling curve, 4+ points | | F4 | | |
| 4 | Sensitivity, 2+ hyperparameters | | F5 | | |
| 5 | Robustness / shift | | F6 | | |
| 6 | Cost table | | table | | |
| 7 (cut first) | Qualitative cases | | F7 | | |

Negative results log (what did not work; one paragraph goes into the main text):

## Pre-registration

- Date criteria and thresholds were frozen:
- What may not change afterwards:
