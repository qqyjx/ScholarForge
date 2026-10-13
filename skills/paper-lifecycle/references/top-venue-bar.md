# Top-venue bar (NeurIPS / ICML / ICLR main track)

Papers at these venues need a finding, a mechanism, and figures. A stack of gates and tables is not enough. Templates for each plan are in `../templates/`.

## 0. Three common failures

1. **Effect smaller than the noise floor.** Gains that are significant only when pooled, single-seed cells, and "flat" sensitivity sweeps that are really under-powered. Referees do not accept "right direction, roughly".
2. **One paper template reused.** "Certify / gate / verify X on modality Y with a conformal-style guarantee" looks fine once. Across several papers, referees see recombination and attack novelty first. Change the contribution type between papers.
3. **A main body made of tables.** With one architecture figure and five to ten tables, referees cannot tell whether the authors understand their results. No analysis figure means no analysis.

## 1. P0: contribution ladder and five questions

A top-venue paper stands on at least two rungs, and not on L2 alone.

| Rung | Content | How referees read it |
|---|---|---|
| L1 Phenomenon | A clean measurement of something not measured before, with a mechanism hypothesis tested once | A finding; can stand alone |
| L2 Method | A principled reason the method should work (not "add a gate") | Alone, it reads as incremental |
| L3 Theory | A theorem that predicts a measurable quantity, confirmed by experiment | Strongest when paired with L1 or L2 |
| L4 Instrument | A new evaluation protocol, noise-floor tool, or benchmark others can use | Counts only with adoption potential |

**Five questions** (answer them in `PROPOSAL.md` before writing):

1. **One figure:** Can the claim be shown in one figure? What does it look like? This becomes Figure 1.
2. **Reversed-result test:** If the result came out the other way, would the paper still stand? If yes, it is a demo, not a hypothesis test. Pick another question.
3. **Three strongest objectors:** Name three recent papers or referee types and what each would say. Map each objection to an experiment.
4. **Effect-size budget:** Expected effect divided by the measured noise floor should be at least 2. Otherwise state the GPU-hours needed to raise n until the effect is decidable. If you cannot compute a budget, the design is not finished.
5. **Why us, why now:** What unique asset do you have (data, tool, theorem, runs already done)? Without one, someone else can reproduce the idea in two weeks.

**Literature:** Scan at least 30 papers from the last 18 months and read at least 8 closely. Build a nearest-neighbor table: neighbor, what they did, the one thing we do that they do not, and their number we will compare against. Fewer than 5 rows means the search is not done. An empty comparison column means the baselines are not decided.

**Gate:** five questions answered, nearest-neighbor table of 5 or more rows, 2 or more ladder rungs, and explicit author approval of the novelty claim. Start the repository only when all four hold.

## 2. P1: experiment floor

Write it in `EXPERIMENT_PROGRAM.md`. Give every cell a budget and a kill order (what to cut first if the budget runs short).

**Core matrix.** The headline must survive here before any extension budget is spent.

- Models: 2 or more families x 2 or more scales, or 3 or more scales in one family.
- Evaluation: 3 or more benchmarks or domains, including at least one mainstream benchmark referees will name.
- Repetition: 3 or more training seeds per cell (not evaluation repeats). Report the noise floor, the spread of same-config reruns, as its own row.
- Baselines: 6 or more, at least 2 from the last 12 months, and always the strongest trivial baseline (no-op, random, majority, strongest training-free).
- Criterion: headline effect of at least 2x the noise floor, with a paired test and a confidence interval. If it falls short, report a null result, not a "trend".

**Extension matrix.** Each item maps to a figure.

| Item | Output | Figure |
|---|---|---|
| Scaling curve | 4 or more scale or data points | F4 |
| Ablation | leave-one-out and cumulative, per component | F5 |
| Sensitivity | 2 or more key hyperparameters, with noise floor | F5 |
| Mechanism | why it works: probes, error taxonomy, decision distributions | F6 |
| Robustness | 1 or more distribution shift or adversarial setting | F6 or table |
| Cost | training and inference GPU-hours, latency, tokens, in the same table as baselines | table |
| Negative results | what did not work, one paragraph in the main text | - |
| Qualitative cases | at least one success and one failure, explained | F7 |

Measure one real unit at full cost before scaling any cell. Do not open the extension matrix until the core matrix has finished. Cut extensions in kill order and name the cuts in Limitations.

## 3. P2: writing skeleton (9-page format)

- The title states the claim. The abstract has at least 3 numbers and one mechanism sentence.
- Figure 1 shows the phenomenon or headline result, not an architecture diagram. The architecture goes in Figure 2 or the method section.
- Introduction: problem, gap (name the papers), one-sentence insight, contributions each followed by where the evidence is ("Fig. 3, Tab. 1"), and a final sentence the reader should remember.
- Method: notation table, algorithm box, one sentence on complexity.
- Experiments: RQ1 to RQn. End each RQ paragraph with a bold one-sentence takeaway. Each RQ has at least one figure or table.
- An analysis section of at least 0.75 page: mechanism, failure cases, negative results.
- Limitations: 2 or 3 items with evidence. Do not undercut the paper.
- `CLAIMS.md`: claim, evidence (figure, table, or macro key), strength (seeds, CI, multiple of the noise floor), status. Every claim must point to a figure or table within 30 seconds. Delete claims that cannot.
- The appendix extends the main text: full result tables, full versions of main figures, proofs, prompts, compute tables, more cases. Significant results stay in the main text.

## 4. P3: figure program

**Main-text floor:** 5 or more figures and 3 or more tables in 9 pages, covering at least 5 of these 7 types.

| Code | Figure | Requirement |
|---|---|---|
| F1 | Phenomenon or headline teaser | Shows the claim at a glance; on page 1 |
| F2 | Method or pipeline | Vector graphics (exported PDF or TikZ) |
| F3 | Main result | Bars or lines with CI; legend order matches the main table |
| F4 | Scale or trend | Scale or budget on x, 4 or more points, noise band |
| F5 | Ablation or sensitivity | One panel per component, or a heatmap |
| F6 | Mechanism or analysis | Distributions, scatter, heatmaps, decision histograms |
| F7 | Qualitative cases | Success and failure, annotated |

- Write `FIGURE_PLAN.md` in P0: number, purpose, data source (results key), generating script, status.
- Generate every result figure from a script. Put the data source hash in the figure file. No hand-typed coordinates.
- Exact values go in tables. Shapes and trends go in figures.
- Count main-text figures, tables, equations, and theorems with a script, not by eye.

## 5. Review rubric for internal reviews

| Dimension | Scale | Question |
|---|---|---|
| Soundness | 1-4 | Claim, evidence, and noise floor agree; the four meaning-audit questions (P4) pass |
| Presentation | 1-4 | Figure 1 stands alone; figures, tables, and text follow one order |
| Contribution | 1-4 | How many ladder rungs; does "we do what they do not" hold against the nearest neighbors |
| Overall | 1-10 | Predicted score per persona, plus one sentence: "what would raise my score by 1" |

End each internal review with a predicted-score table (3 personas x 4 dimensions) and the cheapest step that would add a point. A predicted mean below 6 goes back to P1 or P2 before packaging.

## 6. Oral and best-paper criteria

Orals are roughly 1-4% of accepted papers; each venue names a handful of best papers. The difference from a poster is that an area chair can restate the paper in one sentence and a committee can write the citation in one sentence. Every item below should leave an artifact in the repository.

### Oral: seven criteria (missing 3 or more means poster tier)

| # | Criterion | Artifact |
|---|---|---|
| O1 | A one-sentence claim an AC can restate without reading the paper | The sentence in `PROPOSAL.md` section 8; three personas restate it the same way |
| O2 | A surprise or a closure: overturns a default belief, or answers a named open question | Nearest-neighbor table names who said the opposite, or who posed the question |
| O3 | Evidence beyond the floor: 3 or more model families, scaling curve of 3 or more points, 2 or more out-of-design transfer settings | Oral rows in `EXPERIMENT_PROGRAM.md`, all with results files |
| O4 | A mechanism, not just a number: theory or controlled analysis predicts a measurable quantity, then it is measured | At least one predict-then-measure pair in the analysis section |
| O5 | Clear: Figure 1 stands alone; a referee from a neighboring area can read it without looking things up | F1 in `FIGURE_PLAN.md`; internal Presentation score of 3 or more |
| O6 | Artifact: code, data, and one command that reproduces the main table | `reproduce.sh` at the repository root, run by the package self-test |
| O7 | No "remains unclear": every persona question has an answer in the main text | Every claim in `CLAIMS.md` has a figure or table anchor |

### Best paper: five more

| # | Criterion | How to check |
|---|---|---|
| B1 | Changes a practice or belief; people will cite it as "X showed that ..." | Write that sentence. If you cannot, the paper does not have it |
| B2 | Simple: the core idea fits in 2 minutes; 3 or fewer moving parts | A 2-minute pitch in the README; a list of moving parts |
| B3 | Rigor above the floor: 5 or more headline seeds, CIs everywhere, negative results reported, pre-registered analysis | `PREREG.md` and a noise-floor table |
| B4 | General and timely: holds in 2 or more unrelated settings, and people need it now | O3 transfer settings; dates in the nearest-neighbor table |
| B5 | Compared against recent award papers: 5 award papers from the target venue's last 3 years (from the official list; do not invent) | Award comparison table in `PROPOSAL.md` section 8 |

### Where these plug in

- P0: `PROPOSAL.md` section 8 holds the oral case and the award comparison. A new project that cannot write O1 and O2 should choose another question.
- P1: the oral matrix sits above the core matrix. Do not open it until the core matrix survives.
- P4: each persona also answers "Recommend for oral? (y/n and why)" and "What one thing keeps this from a best-paper nomination?". Treat the paper as oral tier only if the predicted mean is 7 or more with at least one 8.
- Existing drafts that will not change topic: improve framing and depth first (CPU work such as new figures from existing results, analysis sections, predict-then-measure pairs), then schedule GPU work behind running experiments.

### Patterns in recent award papers

These are heuristics from reading recent ICLR outstanding-paper lists and committee citations. Check them against the current official list before relying on them.

1. Titles are often a complete declarative sentence that states the finding, rather than "ACRONYM: method for task".
2. Published committee citations rarely praise beating baselines. They praise filling a gap in understanding, the way the research was done (simple, systematic, well designed), and pushing evidence into real-world settings.
3. Measurement papers that win follow "measure, then mechanism, then prescription". They do not end on caveats.

Two consequences:

- Breadth of evidence (O3) protects against rejection. It is rarely the reason a paper is singled out.
- B1 is often a layout problem. Many drafts can state the sentence that will be cited but do not put it in the abstract. Put a one-sentence setup first and the sentence to be cited second. In the internal review, check whether three personas restating the first three abstract sentences produce the same sentence.
