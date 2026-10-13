// ScholarForge example workflow: sibling-sweep.
// Runs in a Claude Code "Workflow" runtime that provides: agent(), log(), phase(), args.
// Applies one change specification, or checks for one defect pattern, across N sibling paper repositories.
// "apply" mode commits locally and never pushes. A human reviews before release.
export const meta = {
  name: 'sibling-sweep',
  description: 'Sweep one change or defect pattern across sibling paper repositories in parallel. "check" is read-only. "apply" edits, verifies, and commits without pushing.',
  whenToUse: 'Template migrations, batch insertion of a required statement, sweeping sibling papers after a confirmed defect. args: {mode:"check"|"apply", spec:"change or defect description", repos:[...], verify:"latexmk"|"none", commit_message:"..."}',
  phases: [{ title: 'Sweep', detail: 'one agent per repository' }],
}
// Concurrency limit: at most `n` agents run at once.
const plimit = async (fns, n = 3) => {
  const out = []
  for (let i = 0; i < fns.length; i += n) out.push(...(await Promise.all(fns.slice(i, i + n).map((f) => f()))))
  return out
}

// Model tier per role: the sweep is mechanical work with an executable acceptance check.
const TIER = { sweep: 'sonnet' }

const mode = (args && args.mode) || 'check'
const spec = args && args.spec
const repos = args && args.repos
const verify = (args && args.verify) || (mode === 'apply' ? 'latexmk' : 'none')
const commitMessage = args && args.commit_message
if (!spec || !repos || !repos.length) throw new Error('args.spec (change or defect description) and args.repos (list of repositories) are required')
if (mode === 'apply' && !commitMessage) throw new Error('apply mode needs args.commit_message (one message for all repositories, so the sweep can be traced)')

// Repository guard: the agent returns the raw output of `git rev-parse --show-toplevel`; the caller compares it.
const guardRepo = (r, repo, skipOk) => {
  if (!r) return r
  const seen = (r.toplevel || '').trim()
  if (seen === repo) return r
  if (skipOk && skipOk(r)) return r
  throw new Error(`repository guard failed: rev-parse --show-toplevel of ${repo} returned ${seen || '(nothing)'}`)
}

const SWEEP_SCHEMA = {
  type: 'object', required: ['repo', 'toplevel', 'status', 'hits', 'notes'],
  properties: {
    repo: { type: 'string' },
    toplevel: { type: 'string', description: 'raw output of git rev-parse --show-toplevel' },
    status: { type: 'string', enum: ['DONE', 'CLEAN', 'HIT', 'SKIPPED', 'FAILED'] },
    hits: { type: 'array', items: { type: 'string' }, description: 'check mode: evidence of each hit; apply mode: list of changed files' },
    diffstat: { type: 'string' },
    committed: { type: 'boolean' },
    notes: { type: 'array', items: { type: 'string' } },
  },
}

phase('Sweep')
const rows = await plimit(repos.map((repo) => () => agent(
  `You handle one repository in a multi-repository sweep: ${repo}. Mode=${mode}.
Specification (the only task definition; follow it exactly and do not widen the scope):
<<<SPEC
${spec}
SPEC>>>

Precheck rules (if one fails, set status=SKIPPED, explain in notes, and change nothing):
1) The output of "git -C ${repo} rev-parse --show-toplevel" must equal ${repo}. Copy the raw output into the toplevel field, whether or not it matches. The caller compares it independently.
2) If "git -C ${repo} status --porcelain" lists dirty files: in check mode, continue and note them. In apply mode, if a dirty file changed in the last 10 minutes (find -mmin -10), set SKIPPED, because another session may be editing it: leave it, note it, move on. A dirty file that has not changed recently may stay, unless it overlaps with a file the specification changes (then SKIPPED).

${mode === 'check'
    ? 'Check mode: read-only. Search this repository for the defect or pattern in the specification. Add each hit to hits as "file:line excerpt". No hits -> status=CLEAN. Any hit -> status=HIT. Modify no file.'
    : `Apply mode: make the change in the specification. Then:
1) Verify: ${verify === 'latexmk' ? 'run latexmk -pdf in the paper directory (or the repository\'s own build); it must finish with 0 errors;' : verify === 'none' ? 'no compile check is needed for this specification;' : `run: ${verify};`} if verification fails, run git checkout -- . to roll back, set status=FAILED, and write the error in notes.
2) If verification passes: git add -A && git commit -m "${commitMessage}". Never push. Set committed=true, diffstat=summary of git show --stat HEAD, hits=list of changed files, status=DONE.
3) If the repository already has the target state (no diff): status=CLEAN. Do not make an empty commit.`}`,
  { model: TIER.sweep, label: `${mode}:${repo.split('/').pop()}`, phase: 'Sweep', schema: SWEEP_SCHEMA, effort: 'high' }
).then((r) => guardRepo(r, repo, (x) => x.status === 'SKIPPED'))))

const done = rows.filter(Boolean)
const summary = {
  mode, spec_first_line: spec.split('\n')[0],
  counts: {
    total: repos.length,
    done: done.filter((r) => r.status === 'DONE').length,
    clean: done.filter((r) => r.status === 'CLEAN').length,
    hit: done.filter((r) => r.status === 'HIT').length,
    skipped: done.filter((r) => r.status === 'SKIPPED').length,
    failed: done.filter((r) => r.status === 'FAILED').length + (repos.length - done.length),
  },
  rows: done,
}
log(`Sweep finished: ${JSON.stringify(summary.counts)}${mode === 'apply' ? '; committed locally, not pushed; a human releases after review' : ''}`)
return summary
