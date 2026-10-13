# Workflows

ScholarForge defines 11 named multi-agent workflows. Each one turns a single-thread checklist from the skill into parallel work.
Three are included here as sanitized examples: `submit-gate.js`, `review-form.js`, `sibling-sweep.js`.
The other eight are listed so the whole suite is visible. They are not included.

The scripts target the Claude Code Workflow runtime, which provides `agent()`, `pipeline()`, `log()`, `phase()` and `args`. They do not run as plain Node programs.

## The 11 workflows

| Workflow | When to run | What it does | Included |
|---|---|---|---|
| `progress-rollup` | Daily or on demand | Reads each paper repository in parallel and drafts progress-table rows, a deadline countdown and an exception list. Writes drafts only. | no |
| `internal-r1` | 2 to 4 weeks before submission | Runs a six-dimension review and an independent statistics check per paper. Writes a prioritized fix list. Does not edit the paper. | no |
| `review-form` | After fixes, before `submit-gate` | Three independent simulated referees fill in a venue review form. One agent merges and de-duplicates the weaknesses. | yes |
| `figure-inventory` | Before figure work starts | Read-only count of figures and tables, mechanisms described only in text, and spare space. Does not draw. | no |
| `visual-audit` | After figures land, before submission | Scores each figure and table against a visual rubric and attaches cropped renders. Does not fix. | no |
| `adversarial-audit` | 1 to 3 days before submission | Audits every main-table row for value and meaning, and runs three reject-minded referee personas. Reports risks only. | no |
| `submit-gate` | Before every package build | Runs script, bibliography, anonymity, figure and layout checks in parallel. Returns a compliance matrix. Read-only. | yes |
| `sibling-sweep` | After a confirmed defect, or for a template change | Applies one change specification, or checks one defect pattern, across sibling paper repositories. Commits locally, never pushes. | yes |
| `response-assembly` | After reviews arrive | Splits the reviews into points (author response), drafts each answer in parallel using only real artifact numbers, assembles the text, and checks length, numbers and tone. A human writes the final wording. | no |
| `camera-ready-gate` | At acceptance | Before upload: rights, figure renders, metadata, dangling pointers, last-page balance and classification codes. After upload: byte comparison with the local build. Read-only. | no |
| `results-landing` | After experiments finish | Checks that results on the compute host reached the repository, regenerates the macro file, and shows a diff with a zero-deviation check against the artifacts. Does not start runs and does not commit. | no |

## Invariants shared by all workflows

1. **Repository guard.** Every agent that touches a repository reports the raw output of `git rev-parse --show-toplevel`. The caller compares it with the expected path. A guard written only in a prompt can be skipped silently.
2. **Hard and soft criteria stay apart.** What a script or a command can decide goes to `hard_failures`. What needs judgment goes to `soft_advisories`.
3. **No workflow crosses a human gate.** None of them pushes, presses a submit button, or rewrites paper text. Audits and reviews produce reports. A person makes every fix.
4. **Shared repositories.** If a target file changed in the last 10 minutes, the agent reports SKIPPED. Another session may be editing it.
5. **Judgment work stays out.** Figure design, experiment design and novelty decisions belong to the main session. Workflows hold read-only audits and mechanical work with an executable acceptance check.

## Model tiers and concurrency

- Each `agent()` call pins a model by role. Mechanical checks, extraction and validation use the middle tier. Meaning audits, referee personas, figure inspection and synthesis use the top tier.
- Every fan-out goes through `plimit(fns, n)`, which runs at most `n` agents at once (default 3).
- Before a run, estimate the agent count (fixed count per paper times the number of papers) and the token cost, and get the user's approval.

## Reading the example scripts

- `meta` names the workflow and lists its phases.
- `TIER` maps each role to a model tier. Change it to change cost.
- `*_SCHEMA` constants are JSON schemas. The runtime validates each agent reply against them.
- `pipeline(items, stage1, stage2)` runs a precheck per item, then a fan-out per item.
- Replace `my-paper` paths and the `forbidden` list in `args` with your own.
