// ScholarForge example workflow: review-form.
// Runs in a Claude Code "Workflow" runtime that provides: agent(), log(), args.
// Three independent simulated referees fill in a review form; one merge agent de-duplicates the weaknesses.
// It only writes a review file. It never edits the paper.
export const meta = {
  name: 'review-form',
  description: 'Review-form simulation: per paper, three independent referees fill in a venue-style form (summary, soundness, presentation, contribution, strengths, weaknesses, questions, rating, confidence). A merge agent de-duplicates the weaknesses. Scores and lists only; the paper is not edited.',
  whenToUse: 'After fixes are done and before submit-gate. args: {repos:["/path/to/my-paper", ...], date:"20260101", venue:"the venue name"}.',
  phases: [
    { title: 'Review', detail: 'three independent referees per paper (methods and statistics / domain / area-chair reading)' },
    { title: 'Merge', detail: 'one merge agent per paper writes review/review_sim_<date>.md' },
  ],
}
// Concurrency limit: at most `n` agents run at once.
const plimit = async (fns, n = 3) => {
  const out = []
  for (let i = 0; i < fns.length; i += n) out.push(...(await Promise.all(fns.slice(i, i + n).map((f) => f()))))
  return out
}

// Model tier per role.
const TIER = { referee: 'sonnet', merge: 'sonnet' }

const repos = args && args.repos
const date = (args && args.date) || 'undated'
const venue = (args && args.venue) || 'a major ML conference'
if (!repos || !repos.length) throw new Error('args.repos is required, for example {repos:["/path/to/my-paper"], date:"20260101"}')

const REVIEW_SCHEMA = {
  type: 'object',
  required: ['referee', 'summary', 'soundness', 'presentation', 'contribution', 'strengths', 'weaknesses', 'questions', 'ethics_flag', 'rating', 'confidence', 'one_point_up'],
  properties: {
    referee: { type: 'string' },
    summary: { type: 'string', description: '3-6 sentences the authors would agree with' },
    soundness: { type: 'integer', minimum: 1, maximum: 4 },
    presentation: { type: 'integer', minimum: 1, maximum: 4 },
    contribution: { type: 'integer', minimum: 1, maximum: 4 },
    strengths: { type: 'array', items: { type: 'string' } },
    weaknesses: {
      type: 'array', items: {
        type: 'object', required: ['text', 'severity', 'where', 'fixable_by_text'],
        properties: {
          text: { type: 'string', description: 'one weakness, with a page, table number or quoted sentence' },
          severity: { type: 'string', enum: ['major', 'minor'] },
          where: { type: 'string', description: 'Section / Table / Figure / page' },
          fixable_by_text: { type: 'boolean', description: 'true if rewording alone removes it; false if it needs new experiments or data' },
        },
      },
    },
    questions: { type: 'array', items: { type: 'string' } },
    ethics_flag: { type: 'boolean' },
    rating: { type: 'integer', enum: [1, 3, 5, 6, 8, 10] },
    confidence: { type: 'integer', minimum: 1, maximum: 5 },
    one_point_up: { type: 'string', description: 'what the authors could do to raise the rating by one step; one sentence' },
  },
}

const MERGE_SCHEMA = {
  type: 'object', required: ['repo', 'ratings', 'mean_rating', 'merged_weaknesses', 'file'],
  properties: {
    repo: { type: 'string' },
    ratings: { type: 'array', items: { type: 'integer' } },
    mean_rating: { type: 'number' },
    merged_weaknesses: {
      type: 'array', items: {
        type: 'object', required: ['text', 'n_referees', 'severity', 'fixable_by_text'],
        properties: {
          text: { type: 'string' }, n_referees: { type: 'integer' },
          severity: { type: 'string', enum: ['major', 'minor'] }, fixable_by_text: { type: 'boolean' },
        },
      },
    },
    file: { type: 'string' },
  },
}

const PERSONAS = [
  { key: 'stats', name: 'Referee 1: methods and statistics', angle: 'You audit criteria, noise floors, pairing, confidence intervals, seed counts, and whether pre-registered criteria agree with the results. Point every weakness at a specific number or sentence.' },
  { key: 'domain', name: 'Referee 2: domain expert', angle: 'You are a senior researcher in this paper\'s subfield. Judge novelty, the real difference from related work, whether baselines are fair, whether the setup is the accepted one in the field, and whether the conclusions go beyond the evidence.' },
  { key: 'ac', name: 'Referee 3: area-chair reading', angle: 'You read like an area chair. Can the headline claim be derived from the evidence in one step? Do abstract, introduction and conclusion say the same thing? Can the figures and tables be read alone? Are the limitations honest? You are most sensitive to wording problems.' },
]

const refereePrompt = (repo, p) =>
  `You are "${p.name}" for ${venue}. ${p.angle}
Material: the file paper/main.pdf in ${repo} (if missing, the newest built PDF). Read the full text with pdftotext -layout and render pages with pdftoppm to look at figures and tables. If supp.zip or supp/ exists, unpack it under /tmp to read the appendix and the code layout.
Read-only. Do not open review/, docs/, preregistration files, internal notes, or git history. You may see only what a real referee sees. You are one of three independent referees. Do not look for the other opinions.
Fill in the venue's review form. Rating scale: 1=strong reject, 3=reject, 5=marginally below, 6=marginally above, 8=accept, 10=strong accept. soundness/presentation/contribution: 1=poor 2=fair 3=good 4=excellent. confidence: 1-5.
Every weakness must be actionable: say on which page, table or sentence, and say whether rewording can remove it. Do not write generic "more experiments are needed". Write the summary in words the authors would agree with. Write one_point_up as a single sentence.`

const mergePrompt = (repo, reviews) =>
  `Merge the three review forms below into one list for the authors. Write it to ${repo}/review/review_sim_${date}.md (create the directory if needed; write only this one file; change nothing else in the paper).
File structure: 1) score table (referee / rating / confidence / soundness / presentation / contribution); 2) de-duplicated weaknesses, sorted by "number of referees who raised it" then severity, each keeping the most specific original wording and marked fixable_by_text; 3) all questions; 4) the three one_point_up sentences verbatim; 5) the three summaries verbatim.
Add no opinion of your own. Do not change any score. Write the file in English.
The three review forms (JSON):
${JSON.stringify(reviews, null, 1)}`

// One paper at a time; inside a paper the three referees run in parallel (limit 3).
const results = await plimit(repos.map((repo) => async () => {
  const short = repo.split('/').pop()
  const reviews = (await plimit(PERSONAS.map((p) => () =>
    agent(refereePrompt(repo, p), { model: TIER.referee, label: `review:${short}:${p.key}`, phase: 'Review', schema: REVIEW_SCHEMA, effort: 'high' })
  ), 3)).filter(Boolean)
  if (!reviews.length) { log(`${short}: no referee returned`); return null }
  const merged = await agent(mergePrompt(repo, reviews), { model: TIER.merge, label: `merge:${short}`, phase: 'Merge', schema: MERGE_SCHEMA, effort: 'high' })
  log(`${short}: ratings ${reviews.map((r) => r.rating).join('/')} (n=${reviews.length})`)
  return { repo, ratings: reviews.map((r) => r.rating), confidences: reviews.map((r) => r.confidence), merged }
}), 1)

return results.filter(Boolean).map((r) => ({
  repo: r.repo, ratings: r.ratings, confidences: r.confidences,
  mean_rating: r.merged ? r.merged.mean_rating : null,
  top_weaknesses: r.merged ? r.merged.merged_weaknesses.slice(0, 6) : [],
  file: r.merged ? r.merged.file : null,
}))
