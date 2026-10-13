# P6 Review period and author response

- At submission, create a directory for the author response. During the wait, do not change the layout; edits go on a branch.
- Parallel submission check: if a sibling paper is under review at another venue, that is simultaneous review. Before each review phase or decision date, re-check the seven non-overlap items (P0) and the policy statements.

## What author responses can and cannot buy

These points come from tracking scores through a full discussion period and from related cases.

- **Transparency does not raise scores.** Referees may praise candor and still lower or keep their scores. What transparency buys is that nobody raises misconduct. It limits damage; disclosure does not replace a fix.
- **Scores built on unverified breadth get withdrawn.** A referee who scored the paper up for "the breadth and apparent consistency of the empirical comparison" takes the points back when that breadth fails verification. The broader the submitted version claims, the more a later disclosure costs. This is a reason to verify before submission, not to disclose less.
- **Low-scoring referees may not take part.** A referee who starts low may never write another word. Do not center the author response on the lowest score; focus on referees who are still talking.
- **After a referee agrees you fixed X, the score depends on the next gap Y they find, not on X.** An author response can buy acknowledgment; to buy score, remove Y before submission.
- **A weak strength costs more than itself.** When one strength collapses, referees re-examine everything not yet checked, and the verdict becomes "needs a complete, consistently evaluated, multi-seed study". Only list strengths that survive "show me the artifact JSON".

## Corrections: before submission, or all at once

- A series of corrections spread over days signals that the bottom has not been reached. Score drops often cite that "the corrections materially change the central empirical evidence".
- Rule: finish all self-checks before the first author response phase and post corrections in one message. After that, post only "promised experiment landed" updates. New analyses a referee's question forces are answers, not self-disclosures, and are fine.
- **Budget the window from discovery to final text, not from final text to submission.** Review phases can close at the AoE deadline with no grace period. Do not open a new investigation on deadline day; a finding you cannot post is wasted. Any "I can finish this tonight" estimate must include the investigation itself, whose length is unknown in advance. To meet a window, finish checking before it opens.

## Promise only what fits in the window

- An experiment promised in a revision and not delivered gets quoted back ("the promised experiments") as evidence the paper needs a rewrite.
- Before promising, compute GPU-hours per cell x seeds needed x hours left. If it does not fit, write "this is a condition for the next version", not "we will add".

## "Remains unclear" is the one opening

- Read "remains unclear" as an instruction: the referee is telling you what they need to change their verdict. The data to answer often already exists.
- **The answer must cut both ways to be believed.** The same seed-spread analysis can support a large effect (three times the seed range) and undercut a small one (inside the seed range), and may force you to withdraw a word like "significantly" from your own post. One-sided answers are not believed.
- **Do not over-retract either.** If a fixed-seed paired bootstrap cannot speak to differences between configurations, withdraw the word "significantly", not the whole ranking when the remaining effects are 2-3x the seed range. Miscalibrated self-criticism is as inaccurate as overclaiming.

## Correct a referee's causal attribution even when the correction hurts

If a referee links two findings into a wrong causal story, correct it even when the true cause is less flattering. The meta-review will otherwise record a false cause, and meta-reviews follow a paper to later venues.

## Conference-system mechanics

- Two character limits: per-review author response fields can allow 10,000, while official comments and confidential author-AC comments allow 5,000. The error reads `Comment value must NOT have more than 5000 characters` with `Characters remaining: -N`, and N is off by one from Python `len(body)` (a trailing newline is not counted). Check `len(body) <= 4950` to be safe.
- Count characters with Python `len()`, never `wc -c` (which counts UTF-8 bytes).
- Every number in a post needs a verdict JSON on disk first, and the source JSON must be committed to the repository the same day. A result that exists only on a remote machine while the post is public is a gap in the artifact. Pull remote results into the repository and commit them the day they are produced.
- When the review period confirms a problem, sweep sibling repositories for the same problem at once (single-seed sweeps, extreme metrics, training/evaluation environment mismatch tend to recur in papers built from the same code).
