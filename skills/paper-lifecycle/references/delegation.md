# Delegation and verification habits

## Who does what

The main session owns direction: topic choice, novelty, experiment design, pre-registered criteria, figure design, all reader-facing text, interpretation of results, targeted acceptance checks, and communication with the user. It does one- or two-command chores itself instead of writing a brief for them.

Subagents get work matched to the cheapest model tier that can do it. Move up a tier only after a cheaper one has failed.

| Tier | Use for | Examples |
|---|---|---|
| Small | Fixed scripts, no judgment | status snapshots, log tails, artifact counts |
| Medium | Mechanical execution with an executable acceptance check | launching a written run script, aggregating landed results, audit scripts, inserting given text and recompiling |
| Large | Execution that needs judgment | writing new scripts, debugging, meaning audits, referee personas |

- One task, one agent. Write the brief once and completely: background, input paths, the paths the agent may change, deliverables, acceptance commands, and when to stop. Send corrections to the same agent.
- The brief must stand alone. Subagents do not inherit your context.
- Check returned work by running its acceptance commands before you rely on it. If it fails, send it back to the same agent with the specific failure. Do not redo it yourself.
- Cap concurrency per model pool (three is a reasonable default). Set a token budget per agent and have it stop and report when it runs over.
- Do not start whole-round fan-outs (many agents at once) without telling the user the agent count and an estimated token cost first.
- If subagents are unavailable, do the work in the main session and say so.

## Verification habits

Each of these exists because a check once passed without doing anything.

- When you write a new check, make it fail once on purpose before you trust it: remove the `.bbl`, plant a fake `\citep`, change one number and confirm the timestamp moves.
- A zero-hit scan proves nothing until you show the scan ran. Run its self-test, or run it once without the filter as a negative control.
- Many false failures come from the observing tool, not the thing observed:
  - The shell's working directory drifted into another repository. Use absolute paths or `(cd X && ...)`.
  - `$?` was read after a pipe and reports the last command, not the one you care about.
  - `grep` is wrapped or aliased to respect `.gitignore`, so gitignored logs return zero hits. Call the real binary (`command grep`).
  - A page-slack probe reports a saturation value once the body has spilled onto the next page. That value is not slack.
- Never end a commit chain with `... | tail -N && git commit`. `tail` exits 0 and a failing test suite gets committed. Use `set -o pipefail` or capture the status in a variable.
- Generated files must be byte-reproducible. Build twice and compare sha256. If you compare against a reused timestamp, do it after a JSON round trip, because float keys can change.

## Parallel agents and shared repositories

- Parallel agents must not share scratch paths. Give each one a unique temporary directory that includes the repository name, and ask it to report which directory it used. Otherwise one agent reads another agent's unpacked files, and the result looks plausible instead of failing.
- Back up only through git. Scratch copies made by parallel agents overwrite each other.
- Treat other agent sessions on the same machine as teammates. State facts (pid, commit sha, path) and state which paths you will and will not touch.
- Before `git add -A` in a shared repository, check file modification times. A file that changed in the last few minutes is probably being edited by another session. Leave it, note it, and move on.
- Before concluding that a repository has no remote, list all remotes (`git remote -v`), not only `origin`. Before creating any resource, check whether an equivalent already exists.
- Do not push other people's unpushed commits.

## Page-budget mechanics (LaTeX)

- A page probe reads the last page. When the body has spilled, a large "fits" value is the probe's saturation point, not slack. To measure the true margin, wrap the trailing paragraph in `\iffalse ... \fi`, run the probe, and restore the file using an absolute path.
- With `\widowpenalty=\clubpenalty=10000`, a paragraph at a page break moves only in whole splits. Freeing one line may change nothing. Free two lines, or shorten the break paragraph itself.
- A cut removes a line only if it removes more than the paragraph's last-line width. Estimate about 4.4 pt per character in a typical 10 pt serif and cut the last-line width plus about 60 pt.
- Cuts before the last page help only when that page's break paragraph can also move by a whole split. Otherwise TeX stretches the page.
- Shrinking a figure on the last two pages frees space roughly one-for-one. On earlier pages, expect about 0.6 of it to reach the end.
