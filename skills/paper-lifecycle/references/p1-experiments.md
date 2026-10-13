# P1 Experiments

## Three rules

1. **Runs are real.** Real GPUs and the real evaluator. No mocks, synthetic stand-ins, or stubs. Run a small smoke matrix (for example a 0.5B model) end to end before scaling up the main matrix.
   - **An LLM client must never fall back silently.** If the backend is unreachable, raise. Default to `fallback=False`. Allow a fallback only through an explicit environment variable, and when it is on, count every fallback and warn on stderr. A client that quietly swaps in a simulator leaves no trace in the artifacts, so a table labeled "real-LLM evaluation" can contain simulated cells.
   - A health probe caches only "healthy". If it caches "unhealthy", a dead server stays undetected until the cache expires, and silent substitution fills the gap.
   - Write `_provenance.json` in every artifact directory: backend, base_url, the model name the server reports, seed, number of tasks, whether fallback was allowed. Without it, the only way to tell which backend produced a result months later is latency forensics.
2. **Only measured numbers.** Numbers not yet produced stay as TODO comments in the `.tex`. Never write design targets or preset values. Preset values left in a draft tend to survive into the camera-ready.
3. **One source of truth.** Aggregate into `results/results.json`. Each entry points back to a raw dump under `runs/<timestamp>/`. `runs/` is review evidence and goes into the code package.

## Validation checklist

**Uncertainty**

- Every headline number: 3 or more training seeds, mean and standard deviation. Significance: paired permutation test (20k or more permutations) plus bootstrap CI.
- A paired bootstrap with fixed training seeds measures the uncertainty of one set of weights over these scenarios. It does not measure the uncertainty of a configuration or a method. Any claim across configurations, methods, or ablation arms needs training seeds in the denominator. A single-seed cell has no interval at all; you cannot even say "not significant".
- Measure two scales before judging an effect: the spread across training seeds for one configuration, and the spread from re-evaluating fixed weights twice (pure evaluation noise). The first is often several times the second. An effect inside the seed range is not a finding.
- Robustness claims cost more than performance claims. A "flat" sweep on a small sample is the default output of noise. Without per-cell seed repeats, write "we did not detect sensitivity", not "insensitive".

**Does the metric measure what the paper says?**

- Trace every metric name in the paper to the field the code actually computes. Search the artifact JSON for the paper's numbers field by field; the field that reproduces them is the one being reported. A "violation rate" can turn out to be an error rate that counts violations and failures together.
- The proposed method and the baselines must run the same checker. List every writer of the metric field: `grep -rn "<metric>.append\|<metric> =" --include=*.py`. If your own method is missing from that list, for example because it hard-codes an empty violation list, its metric is zero by construction.
- The "do nothing" anchor must run on the main protocol, not on a different harness. If a no-op agent scores the same as the method, the method's number shows nothing.
- Treat extreme values (0.0%, 100%, perfectly monotone, perfect separation) as a bug until disproved.
- After loading a reference set (gold labels, allow-list, benchmark set), `assert` that it is non-empty, and check one known positive and one known negative. Tolerant code such as `r.get("task") or {}` turns a missing field into an empty gold set, and the metric silently changes meaning.
- Use a general criterion before a clever one. For example, latency per step separates a simulator (about 0.1 s) from a real model (seconds) across the whole table at once. A clever criterion such as matching a template string can only corroborate; it cannot bound the extent of a problem.
- A docstring or comment that says two quantities are "comparable" is not evidence. Check the artifact metadata (seeds, encoder, denominators) against the paths the paper names.
- Unusual instrument readings get an independent re-check before anyone acts on them. A reading that contradicts three other pieces of evidence and does not reproduce in isolation is probably an instrument artifact; recompute with a different method (for example blockwise float64).
- Zero-change or always-zero results need a liveness check: distribution of action magnitudes, fraction of non-zero actions, action entropy. An agent whose adjustments are always zero never acts, and its perfect safety number is void. Share liveness checks across repositories as a tool instead of rewriting them per project.

**Controls and protocols**

- A control arm must match the working statistic of the mechanism. Otherwise it compares "mechanism on" versus "mechanism off", not the property you meant to isolate. Example: if coordination fires when cosine similarity exceeds 0.7, semantic embeddings (mean cosine about 0.94) always fire and random vectors (cosine near 0) never do, so "semantic versus random" contains no semantic contrast. The fix is a code that matches the statistic but carries no semantics. A control that resamples its random code on every call is a memoryless channel, not a code; the code must be deterministic in the message.
- Declare a "unified protocol" layer by layer: same backbone, same training environment version, same evaluation environment version, same criterion, same checkpoint selection rule, same budget. "Evaluated under one fixed simulator commit" will be read as covering evaluation only. Trace read-only through artifact adapter fields, checkpoint timestamps, and training log names.
- The same weights are not comparable across evaluation rounds or scenario sets. Before quoting a number across tables, compare the scenario ID sets one by one (not their counts), the evaluation round, and the evaluation flags. Across different scenario sets compare spreads, not levels, and say so in the text.
- Baseline protocol must match yours exactly: n, token limit, evaluator version, batch size. Rows copied from published numbers are labeled "published, different protocol" and are excluded from any "surpasses every baseline" sentence. Your method and the baselines must use the same channel or medium.
- Pin the model version of any LLM judge and average over A/B order swaps. A version change shifts absolute scores and can flip rankings.
- Compare methods on the same prompt, image, or task with paired tests. With several seeds on the same prompt, use prompt-clustered inference. An estimator that is zero on most arms has too little resolution; raise the resolution before concluding.

**Costs and long runs**

- Before extrapolating cost, diff the two code paths. A "fast" and a "full" function with the same name are two algorithms until shown otherwise. Before scaling any parameter, measure one real unit at full cost.
- Sweeps of an hour or more checkpoint every cell (append and fsync to a `.jsonl`; rerunning the same command resumes). Run them on a machine with independent power. A script that writes results only at the end loses everything on a power cut.

**Theory and scope**

- Every assumed quantity in a theorem needs a measured value or an "unverified" label. The theorem's configuration must equal the run configuration. A theorem proved for one parameter value while every experiment uses another will be flagged as fundamental. Referees treat unmeasured assumptions (bounded false clearance, bounded TV distance, decorrelation) as vacuous. List assumption, measured value, artifact key; turn any row you cannot fill into a remark or drop the theorem.
- Planned, queued, or "for the camera-ready" experiments do not go into the paper. RQs describe only what has run. The appendix has no empty tables.
- An all-zero or floor result is a diagnostic. Report it honestly and switch to an evaluation that can discriminate. Do not hand-edit numbers.

**Table self-consistency**

- Mean, standard deviation, and maximum in a results table can falsify each other. In a sample of n, no point lies more than (n-1)/sqrt(n) sample standard deviations from the mean (Samuelson's inequality; 2.846 for n=10, 1.155 for n=3). A transcription error often breaks this by a wide margin. An author's confirmation that a value is right is not proof that the numbers are consistent; check the arithmetic anyway.
- Also compare every value reported for the same condition in more than one table.
- When a row is inconsistent, recompute it from the per-sample data. Substitute a suspected wrong value for each cell in turn; the substitution that reproduces the old mean, std, and max locates the error. Store the per-sample data as a comment in the `.tex` so the row is traceable.
- Both checks are plain arithmetic. A 20-line script that parses the `.tex` tables is enough.

**After a code fix**

- If a bug fix was followed by rerunning only part of the experiments, partition the paper by the code version that produced each result. Never mix results from before and after the fix.
  1. Use invariants to confirm old and new results come from the same experiments.
  2. Replace numbers that have corrected data, and pin the source file name in a `.tex` comment.
  3. Mark the rest `PENDING RERUN` and list them as blockers. Never present old numbers as results of the fixed code.
  4. A fix can reverse the direction of a claim. Rewrite the abstract, highlights, and conclusion, not only the numbers. Re-read the new figures: qualitative statements can reverse too.
- If the fix makes the original evaluation panel unusable (for example some scenarios no longer converge) and a new panel is used, all of these are required:
  1. Both arms (treatment and control) are re-aggregated on the same panel.
  2. If a dropped scenario held an extreme value the paper discussed, say that the panel maximum understates the upper tail, and keep the old value as a reference.
  3. Document how the panel was selected (solvability, not outcomes) in the text.
  4. Figure captions state "mean over N scenarios with min-max band".
  5. Compare every effect size with the solver tolerance. An effect inside the tolerance is a null result, not a ranking.
- Two independent legacy batches of the same configuration can differ slightly. Report that as reproducibility spread; do not "correct" one against the other.
