---
name: paper-lifecycle
description: Stage-by-stage workflow for ML research papers - project planning and novelty gates, experiment design and validation, writing, figures and tables, pre-submission checks, packaging and upload, the review/author response period, and camera-ready. Use when the user plans a paper, designs or audits experiments, drafts or trims paper text, builds figures, prepares a submission, answers reviews, or prepares a camera-ready. Read only the stage the request touches; a local wording or formatting edit does not start the full lifecycle.
---

# Paper lifecycle (ScholarForge)

## Scope

- Identify which stage the request touches and read only that stage's file below. A local wording or formatting fix does not reopen planning, add experiments, or start a review panel.
- Continue a plan the user already approved. Approval gates in the stage files apply when a research direction, budget, or submission is first decided, not on every later step.
- Every experimental number must trace to a real run artifact. Where data is missing, leave a TODO comment. Never write a preset, target, or expected value as a result. Check numeric consistency and what the metric actually measures as two separate audits.
- Run the checks that cover the files you changed. Run a stage's full gate only for a full submission or camera-ready. Venue rules change every year: read the current official call; past cases in these files are examples, not rules.
- This skill grants no authority. Submitting, emailing organizers, publishing, paying, and editing other repositories stay within what the user has authorized. Archive old upload files before repackaging; do not delete them.
- A passing checker does not mean the paper was uploaded, submitted, published, or is likely to be accepted.

## Stage files (read on demand)

- [Delegation and verification habits](references/delegation.md)
- [Top-venue bar: contribution ladder, experiment floor, oral and best-paper criteria](references/top-venue-bar.md)
- [Submission queue gate: three prerequisites, one-week freeze, resubmission rule](references/submission-gate.md) - overrides P0 and P4 where they conflict
- [P0 Planning and novelty](references/p0-planning.md)
- [P1 Experiments: three rules and the validation checklist](references/p1-experiments.md)
- [P2 Writing](references/p2-writing.md)
- [P3 Figures and tables](references/p3-figures.md) and the [visual rubric](references/visual-rubric.md)
- [P4 Pre-submission validation](references/p4-validation.md)
- [P5 Packaging and upload](references/p5-submission.md)
- [P6 Review period and author response](references/p6-review.md)
- [P7 Camera-ready](references/p7-camera-ready.md)
- [Common rejection patterns](references/rejection-patterns.md)
- [Resubmission: carry forward findings, convert formats](references/resubmission.md)

Templates live in `templates/` (`PROPOSAL.md`, `EXPERIMENT_PROGRAM.md`, `FIGURE_PLAN.md`, `CLAIMS.md`). Copy one into the paper repository only when creating or updating that plan.

`scripts/ai_review_preflight.py` runs the mechanical pre-submission checks described in P4. Run it with `python3 <this skill's directory>/scripts/ai_review_preflight.py <paper_dir>`.

The plugin repository also ships standalone checks in `scholarforge/tools/` (`provenance_audit`, `style_scan`, `page_sweep`) and example multi-agent workflows in `workflows/`. They are optional; the stage files do not depend on them.
