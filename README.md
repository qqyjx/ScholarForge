# ScholarForge

**An agent-driven system for the full research-paper lifecycle, built on Claude Code.**

> This repository is a sanitized demo of a personal research workflow; it contains no paper content, no experiment results and no private configuration. It illustrates the method. It is not the code used for any paper's experiments and it does not reproduce any number reported in any paper. The toy paper in `examples/toy-paper/` is synthetic.

ScholarForge is a Claude Code plugin plus a few runnable checks. The plugin holds one skill, one subagent and a set of regression evals. The repository also holds example multi-agent workflows and a small offline demo.

## Why

- **Every number traces to an artifact.** A number in a paper is one LaTeX macro. Each macro is tied to a key in a run-artifact file. A number with no artifact is a failure. Where data is missing, the draft keeps a TODO and never a guess.
- **Stage gates.** The skill has eight stages (P0 to P7), from planning to camera-ready. Each stage file has criteria and acceptance gates. A request loads only the stage it touches. A wording fix does not start a full review.
- **Multi-agent review, with limits.** Named workflows fan out audits and simulated reviews in parallel. They are read-only or commit locally. A human makes every fix and presses every submit button.

## Components

| Component | Where | What it is |
|---|---|---|
| Skill | `skills/paper-lifecycle/` | Eight lifecycle stages (P0 planning, P1 experiments, P2 writing, P3 figures, P4 validation, P5 submission, P6 review and author response, P7 camera-ready), plus references for the top-venue bar, the submission queue gate, rejection patterns, resubmission, delegation and a visual rubric. Four templates. One preflight script. |
| Subagent | `agents/paper-executor.md` | Executes a self-contained brief and reports what it verified. Carries the rules on numbers and verification. |
| Evals | `evals/` | Seven regression cases for the skill. Four check behavior on paper tasks. Three check that the skill stays out of the way. |
| Workflows | `workflows/` | 11 named multi-agent workflows are described in a table. Three are included as sanitized scripts: `submit-gate.js`, `review-form.js`, `sibling-sweep.js`. |
| Tools | `scholarforge/tools/` | `provenance_audit` (macro to artifact check), `style_scan` (filler phrases), `page_sweep` (page budget). Standard library only. Each has `--selftest`. |
| Demo | `scholarforge/demo.py` | An offline run on a synthetic toy paper. |

The 11 workflows are: `progress-rollup`, `internal-r1`, `review-form`, `figure-inventory`, `visual-audit`, `adversarial-audit`, `submit-gate`, `sibling-sweep`, `response-assembly`, `camera-ready-gate`, `results-landing`. See `workflows/README.md`.

## Quickstart

Load the plugin for one session:

```bash
git clone <this repository> scholarforge
claude --plugin-dir ./scholarforge
```

Then ask about a paper task, for example "review my experiment plan for an ICLR submission". You can also call the skill by name: `/scholarforge:paper-lifecycle`. To check the plugin files:

```bash
claude plugin validate ./scholarforge
claude plugin eval ./scholarforge --runs 1 --no-publish
```

Run the offline demo. It needs Python 3.10 or newer, no network and no API key. It takes well under a second:

```bash
cd scholarforge
python -m scholarforge.demo
python -m pytest -q          # needs pytest
```

The demo does four things on `examples/toy-paper/`:

1. **Provenance check.** Each number macro in `main.tex` must equal its artifact value in `results/*.json`, formatted once from the raw value. It flags a stale macro and a planted hard-coded number.
2. **Style scan.** It flags planted filler phrases.
3. **Mock submit-gate.** An orchestrator runs four checks (provenance, style, layout, anonymity) through a bounded worker pool and prints a compliance matrix. It has the same structure as `workflows/submit-gate.js`: precheck, repository guard, parallel gates, schema check, verdict.
4. **Control run.** The same gate runs on a repaired copy of the toy paper and must report CLEAN. This shows the checks can pass.

Each tool also runs alone:

```bash
python -m scholarforge.tools.provenance_audit --tex examples/toy-paper/main.tex --map examples/toy-paper/macros_map.json
python -m scholarforge.tools.style_scan examples/toy-paper --lines
python -m scholarforge.tools.page_sweep --tex examples/toy-paper/main.tex --limit 1
```

## Model tiers

Delegation uses the cheapest model tier that can do the job. A job moves up a tier only after a cheaper one has failed.

| Role | Tier |
|---|---|
| Direction, novelty, experiment design, reader-facing text, final checks | Main session (top tier, high reasoning effort) |
| Mechanical work with a fixed acceptance check: log reading, extraction, file moves, given commands | Small model (Haiku) |
| Work that needs judgment inside a brief: new scripts, evaluations, table generators, gates | Middle model (Sonnet) |
| Figures and drawings | Opus at high effort |

A blind benchmark of figure models chose the figure configuration. The benchmark data is not part of this repository.

The workflow scripts pin a model per role with a `TIER` constant and cap concurrency with `plimit` (3 by default). Tell the user the agent count and an estimated token cost before a fan-out starts.

## Repository layout

```
.claude-plugin/plugin.json     plugin manifest
skills/paper-lifecycle/        SKILL.md, references/, templates/, scripts/
agents/paper-executor.md       subagent
evals/                         seven regression cases with graders
workflows/                     README.md and three example workflow scripts
scholarforge/                  Python package: tools/, orchestrator.py, submit_gate.py, demo.py
examples/toy-paper/            synthetic paper, run artifacts and macro map
tests/                         pytest suite
```

## Simplifications

- The demo has no model calls. The "agents" in `orchestrator.py` are local functions. The tier labels are printed, not used.
- The mock submit-gate has four gates. The workflow script has five (scripts, bibliography, anonymity, figures, layout). The figure and bibliography gates need a model or network access and are not in the demo.
- The layout gate estimates pages from a word count. A real check reads the compiled PDF (`page_sweep --pdf`).
- The provenance check flags decimals and percentages in the body. It does not flag integers such as counts. A line ending in `% prov:ok` is exempt.
- The workflow scripts need the Claude Code Workflow runtime. They are examples and are not tested here beyond a syntax check.

## Limitations

- A passing check does not mean a paper was uploaded, submitted, published or will be accepted.
- The checks find mechanical problems: unmatched numbers, filler phrases, page budget, leaked strings. They do not judge novelty, soundness or whether a metric measures what the text says.
- The skill reflects one author's practice. Venue rules change every year. Read the current call for papers; the cases in the stage files are examples, not rules.
- The workflows were written for one setup and sanitized for this repository. Expect to change paths, scripts and model names.
- The macro-to-artifact rule only helps if the artifact files are real run outputs. The tools check that a macro matches a file. They do not check that the file came from a real run.

## License

MIT. Copyright (c) 2026 Yifan Xiao.
