// ScholarForge example workflow: submit-gate.
// Runs in a Claude Code "Workflow" runtime that provides: agent(), pipeline(), log(), phase(), args.
// Read-only: the gate never builds a package, never commits, never submits.
export const meta = {
  name: 'submit-gate',
  description: 'Submission-package compliance gate: scripts, bibliography, anonymity, figures and layout run as five parallel checks per paper; prints a compliance matrix. Read-only.',
  whenToUse: 'Before every package build. Single paper: {repo:"/path/to/my-paper", venue:"ICLR"}. Several papers: {repos:[...], venue}. About 6 agents per paper.',
  phases: [
    { title: 'Precheck', detail: 'repository identity and environment' },
    { title: 'Gates', detail: 'five parallel checks per paper' },
  ],
}

// Concurrency limit: at most `n` agents run at once. Fan-outs go through plimit.
const plimit = async (fns, n = 3) => {
  const out = []
  for (let i = 0; i < fns.length; i += n) out.push(...(await Promise.all(fns.slice(i, i + n).map((f) => f()))))
  return out
}

// Model tier per role: mechanical checks run on the middle tier, figure inspection on the top tier.
const TIER = { mechanical: 'sonnet', inspection: 'opus' }

const repos = (args && (args.repos || (args.repo ? [args.repo] : null))) || null
if (!repos || !repos.length) throw new Error('args.repo or args.repos is required, for example {repo:"/path/to/my-paper", venue:"ICLR"}')
const venue = (args && args.venue) || ''
// Strings that must not appear in an anonymous package. Supplied by the caller.
const forbidden = (args && args.forbidden) || ['my-name', 'my-institution', '/home/']

// Repository guard. The agent reports the raw output of `git rev-parse --show-toplevel`.
// The caller compares it with the expected path, so a guard written only in a prompt cannot be skipped silently.
const guardRepo = (r, repo, skipOk) => {
  if (!r) return r
  const seen = (r.toplevel || '').trim()
  if (seen === repo) return r
  if (skipOk && skipOk(r)) return r
  throw new Error(`repository guard failed: rev-parse --show-toplevel of ${repo} returned ${seen || '(nothing)'}`)
}

const PRE_SCHEMA = {
  type: 'object', required: ['ok', 'toplevel', 'paper_dir', 'main_tex', 'pdf_path', 'notes'],
  properties: {
    ok: { type: 'boolean' }, paper_dir: { type: 'string' }, main_tex: { type: 'string' },
    toplevel: { type: 'string', description: 'raw output of git rev-parse --show-toplevel' },
    pdf_path: { type: 'string' }, figure_count: { type: 'integer' }, dirty: { type: 'boolean' },
    notes: { type: 'array', items: { type: 'string' } },
  },
}

const GATE_SCHEMA = {
  type: 'object', required: ['gate', 'verdict', 'hard_failures', 'soft_advisories', 'evidence'],
  properties: {
    gate: { type: 'string' }, verdict: { type: 'string', enum: ['PASS', 'FAIL', 'WARN'] },
    hard_failures: { type: 'array', items: { type: 'string' } },   // machine-checkable, must be fixed
    soft_advisories: { type: 'array', items: { type: 'string' } }, // judgment items for a human
    evidence: { type: 'array', items: { type: 'string' } },
  },
}

const ownership = (repo) => `Precheck rules (do these first; if one fails set ok=false, explain in notes, and stop):
1) The output of "git -C ${repo} rev-parse --show-toplevel" must be exactly ${repo}. Copy the raw output into the toplevel field, whether or not it matches. The caller compares it independently.
2) If the names in "git -C ${repo} remote -v" clearly do not match the directory name, add HEAD_MISMATCH to notes.
3) This whole workflow is read-only. Do not modify files in the repository. Do not commit or push. Compile or unpack only under /tmp.`

const results = await pipeline(
  repos,
  // Stage 1: one precheck agent per paper.
  (repo) => agent(
    `${ownership(repo)}
After the precheck, locate: the paper directory (usually paper/ or the directory with main.tex), main.tex, the newest built PDF that matches main.tex, and the number of figure files. Set dirty=true if "git status --porcelain" is not empty. Set ok=true only if the precheck passed and main.tex exists.`,
    { model: TIER.mechanical, label: `pre:${repo.split('/').pop()}`, phase: 'Precheck', schema: PRE_SCHEMA, effort: 'high' }
  ).then((pre) => guardRepo(pre, repo, (x) => x.ok === false)),

  // Stage 2: five parallel gates per paper, at most three at a time.
  async (pre, repo) => {
    const name = repo.split('/').pop()
    if (!pre || !pre.ok) return { repo, verdict: 'SKIPPED', precheck: pre, gates: [] }
    const ctx = `Repository=${repo}; paper directory=${pre.paper_dir}; main.tex=${pre.main_tex}; built PDF=${pre.pdf_path}; target venue=${venue || 'not specified'}.
Read-only: do not change files in the repository, do not commit, do not push. Write temporary files to /tmp.
Return structured results. hard_failures = problems that must be fixed before submission (one per item, with file and location). soft_advisories = items for a human to check. evidence = short excerpts of key command output.
Verdict: any hard_failures -> FAIL; only soft_advisories -> WARN; otherwise PASS.`
    const gates = await plimit([
      () => agent(`${ctx}
You run the script gate. Set gate to "scripts". Run, in order:
1) python -m scholarforge.tools.provenance_audit --tex ${pre.main_tex} --map <macros_map.json> (every number macro must resolve to a run-artifact value)
2) python -m scholarforge.tools.style_scan ${pre.paper_dir}
3) the repository's own self-check script, if one exists (for example "make check")
A last line RESULT=PASS or RESULT=FAIL is the hard criterion. Copy each [FAIL] line into hard_failures and each [WARN] line into soft_advisories. If a script cannot run, record that as FAIL with the error text. Do not bypass a broken script.`,
        { model: TIER.mechanical, label: `scripts:${name}`, phase: 'Gates', schema: GATE_SCHEMA, effort: 'high' }),
      () => agent(`${ctx}
You run the citation gate. Set gate to "bib".
1) Lint every .bib file under the paper directory (duplicate keys, missing required fields, malformed names).
2) Search the newest compile log for "undefined citation" and "empty citation". If the log is older than main.tex, say so.
3) Report entries whose DOI or arXiv id does not resolve as soft_advisories (a network failure is a soft_advisory, not a failure).
Structural errors go to hard_failures. Suspicious entries go to soft_advisories with the cite key.`,
        { model: TIER.mechanical, label: `bib:${name}`, phase: 'Gates', schema: GATE_SCHEMA, effort: 'high' }),
      () => agent(`${ctx}
You run the anonymity gate for double-blind review. Set gate to "anon". Four scans:
1) Built PDF, object level: read docinfo (/Author and others) and XMP metadata with a PDF library, then search the extracted text for these strings: ${forbidden.join(', ')}. Hits inside third-party citations do not count. Hits in the author block, acknowledgments or page headers do.
2) Code package: unpack any submission archive under /tmp and search all files for the same strings. If no archive exists, scan the source directory that will be packaged.
3) Every figure PDF: check /Author and XMP metadata at object level. Exported slide figures often carry a real author name that pdfinfo does not show.
4) Traces of another venue: search the text and code package for names of other venues (citations excluded). Also look for helper scripts that should not ship.
Any hit in 1, 3 or 4 is a hard_failure.`,
        { model: TIER.mechanical, label: `anon:${name}`, phase: 'Gates', schema: GATE_SCHEMA, effort: 'high' }),
      () => agent(`${ctx}
You run the figure gate. Set gate to "figures". Copy ${pre.pdf_path} to /tmp first.
1) Resolution: list embedded bitmaps with pdfimages -list, combine with the printed width, and report every image below 300 effective DPI. Vector figures have no such problem.
2) Rendered inspection: render pages that contain figures to PNG at 150 dpi and look at each one. Check spelling, leftover template text, overlapping legends, labels that differ from the body text, and text smaller than 6 pt. Text extraction misses these defects, so inspect the rendered pages.
3) Spot-check that symbols inside figures match the equations in the text (soft).
Clear spelling errors, template leftovers and low DPI are hard_failures. Doubtful font size or style items are soft_advisories. Name the page and figure for each item.`,
        { model: TIER.inspection, label: `figures:${name}`, phase: 'Gates', schema: GATE_SCHEMA, effort: 'high' }),
      () => agent(`${ctx}
You run the layout gate. Set gate to "layout". Copy ${pre.pdf_path} to /tmp first. Do not rebuild.
1) Pages: read the total page count with pdfinfo and find the page where References starts. Apply the page limit of the target venue from its current call for papers. If the venue is unknown, report the numbers and do not judge.
2) Check that the checklist is not \\input into the body.
3) Count "Overfull \\hbox" in the newest .log file (say if the log is stale).
4) Last-page column balance (two-column templates only): compare the lowest text position of the left and right column on the last page. A gap over 100 pt is a soft_advisory.
5) Style red lines in the body (soft): bullet lists in the body, mixed \\paragraph and \\subsubsection.
Exceeding the page limit or a checklist inside the body is a hard_failure.`,
        { model: TIER.mechanical, label: `layout:${name}`, phase: 'Gates', schema: GATE_SCHEMA, effort: 'high' }),
    ])
    return { repo, precheck: pre, gates: gates.filter(Boolean) }
  }
)

// Compliance matrix: one verdict per paper.
const matrix = results.filter(Boolean).map((r) => {
  const verdict = r.verdict === 'SKIPPED' ? 'SKIPPED'
    : r.gates.some((g) => g.verdict === 'FAIL') ? 'BLOCKED'
    : r.gates.some((g) => g.verdict === 'WARN') ? 'WARN' : 'CLEAN'
  return { ...r, verdict }
})
log(`Compliance matrix: ${matrix.length} papers, BLOCKED=${matrix.filter((m) => m.verdict === 'BLOCKED').length}, CLEAN=${matrix.filter((m) => m.verdict === 'CLEAN').length}`)
return { venue, matrix }
