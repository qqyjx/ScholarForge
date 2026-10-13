# P4 Pre-submission validation

- **Pass the [submission queue gate](submission-gate.md) first** (necessity matrix, theorem assumption table, an artifact key for every number). Freeze new experiments seven days before the deadline; every check below runs on frozen artifacts.
- Run a self-check over the repository: leftover placeholders, undefined citations, overfull boxes, page count, provenance. It passes only with zero FAILs.
- **Adversarial self-review before submission.** Take the role of a referee who wants to reject the paper. Attack the source of every number in the main table (which JSON, which adapter, which scenario set, how many seeds, whether training and evaluation used the same environment version), not the writing. Audits of this kind usually need no new GPU time, only re-parsing existing artifacts, and they can be done the day before submission. Done early, the paper gets smaller but true. Skipped, the review period collects the difference as lower scores (see P6).
- **Every row in the main table must answer "show me the artifact JSON" on the spot.** Delete rows that cannot, before submission. Do not keep them for breadth.

## Value audit and meaning audit are different

1. **Value audit:** can every number in the paper be traced to an artifact field? This checks transcription.
2. **Meaning audit:** what does that field actually measure? This checks validity.

Four fixed questions for the meaning audit:
1. Does the metric name trace to the field the code really computes?
2. Do the method and the baselines run the same checker?
3. What does the no-op anchor score on the main protocol?
4. If the method's core module is switched off, does the number change?

A value audit cannot, by design, catch an artifact that measures nothing. A number can match its JSON exactly while the agent behind it never acted: for example, an LLM planner whose output fails to parse every time, a fallback plan with symbolic placeholders instead of values, missing increments filled with zero, and a world model mapping every candidate to the same zero vector. A strong warning sign: a large perturbation leaves per-seed results identical to the last digit.

"Experiments completed" must mean the meaning audit passed, not that every TODO box is checked. A gate list without a meaning-audit line proves only that transcription is correct.

## Fixes after an audit get an independent re-check

A common failure: an audit lists blocking items and fixes, each item is edited and reported fixed, and an independent re-check later finds many unresolved, some of them new errors introduced by the fix (an abstract saying "nowhere significantly above" when one cell has p=1e-4; a maximum reported as "on average"; a replacement sentence copied from the audit that contradicts the git history). Three rules:

1. **Changing wording is not changing facts.** An item closes when the text's claim equals the claim the artifacts support, not when the flagged sentence is replaced. Every fix row records file:line, before -> after, and the artifact key behind each number. A number without an artifact key does not enter the text.
2. **New sentences get their own value and meaning audit.** Check each quantifier (all, nowhere, on average, at most) against its macro source. A macro that takes a max cannot support "average". One significant cell rules out "nowhere".
3. **Whoever fixes does not report "fixed".** A separate agent or session re-checks each item against current files and an unpacked, executed package, and marks it RESOLVED / COSMETIC / UNRESOLVED / AUDIT-WRONG. Report only RESOLVED items as done. Report AUDIT-WRONG too: auditors also err.

## Format and anonymity

- Read the current call for papers for page structure word by word (for example: main text at most 7 pages, pages 8-9 references only). Upload a checklist separately if required; never `\input` it into the main text, where it counts toward the page limit.
- One source, several outputs: a switch in `main.tex` produces the supplementary (appendix-only, with `xr` to keep theorem numbers in sync) and the checklist. Compile `main` first. After `latexmk -C`, rebuild every output.
- Four anonymity scans: (1) the final PDF at object level with pikepdf for `/Author`, real names, affiliations; (2) the code package for usernames, absolute paths, hostnames, internal IPs, logs; (3) metadata inside figure PDFs; (4) text overlap with sibling papers.
- **Style fingerprint scan across sibling papers:** compare 8-grams across papers and 5-grams shared by three or more, after stripping TeX. Boilerplate blocks (AI use, reproducibility, ethics statements) tend to be rewrites of one paragraph; a referee who gets two of them notices. Write each statement fresh. Several papers citing the same set of self-citations is a stronger de-anonymization signal than shared phrases; cite only self-work with a defensible connection, and do not make the sets identical.
- Make every gate fail once on purpose before trusting it. Show a zero-hit scan actually ran.

## Automated-review rehearsal

Some venues now attach an automated AI review to each submission. It reliably catches:
1. Uncited nearest neighbors (2-5 per paper), phrased as "Section 5 calls X the closest existing theory, despite Y".
2. Theorems that contradict their remarks or corollaries.
3. Statistical tests that do not match the pairing structure of the data.
4. Numbers in the text that disagree with tables or figures.
5. Headline sentences contradicted by the paper's own tables.

The mechanical part is scripted: `python3 <skill dir>/scripts/ai_review_preflight.py <paper_dir>`. FAIL covers planned-experiment sentences, LLM-tell density, blanket superlatives, abstract numbers with no source, no seeds or spread, fewer than 5 references from the last two years, and leftover placeholders. WARN covers assumptions without a measurement pointer, undefined acronyms, and dash density. A non-zero exit blocks packaging.

The semantic parts (1, 2, 5) need referees: three simulated referees using the venue's review form, an adversarial self-review, and one persona dedicated to missing nearest neighbors (for each contribution, find the three closest papers from the last two years and check whether each is cited and distinguished). Fix any hit before submitting.

- **"What is sold equals what is measured."** For every named component in the abstract (signal, correction term, training stage, constraint), find its measurement row in the experiment matrix. If there is none, remove it from the abstract.
- **Assumption table:** theorem assumption -> measured value, artifact key, or "unverified". Put it in the supplementary as a fixed table and summarize it in one sentence in the main text.
