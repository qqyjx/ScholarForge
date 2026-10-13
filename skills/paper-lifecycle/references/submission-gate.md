# Submission queue gate

Most rejections trace back to five causes: submitting before the evidence exists, claims stronger than the proofs, checks that exist but are never closed, the wrong venue or format, and basic compliance mistakes. The first two decide acceptance. The last three decide how much time is wasted.

The rules below are hard rules. They run alongside P0, P4, and the resubmission rules. Where they conflict, this file wins.

## 1. Three prerequisites before a paper enters any submission queue

Before a paper appears on any deadline list, the repository must already contain:

- **Necessity matrix readout.** For each architectural component, one "remove it" ablation, plus the simplest non-learned or fixed baseline. A script generates the readout from artifacts. If removing a component costs nothing, or the simple baseline matches, change the claim first.
- **Theorem assumption table.** For every assumption of every theorem: the measured value, the artifact key, or an explicit "unverified". A theorem with an unverified assumption does not appear in the abstract or the contribution list.
- **An artifact key for every number in the main text.** A results file that says it is "not yet traceable", or that was created before the experiment code was committed, counts as no artifact. One untraceable number keeps the whole paper out of the queue.

If any of the three is missing, there are two options: move to the next deadline, or publish a technical report. Do not submit anyway. An approaching deadline is not an exception.

## 2. Freeze new experiments one week before the deadline

From seven days before the deadline, start no new experiment cells. GPUs run only reproductions and fill in missing artifact links. That week is for meaning audits, independent re-checks, rewriting, style, and page budget.

Reason: numbers added in the last days are the ones nobody has time to check, and they are the ones that reach the paper unchecked. Record the freeze date in the resubmission plan and the deadline list. Mark queued cells after the freeze date as `post-freeze`; they are for the author response only.

## 3. Finish the experiments, then submit

A paper does not enter any queue until every experiment registered in its plan or pre-registration has landed and been read. The deadline is not a reason to submit. Finished experiments are. Papers that are not done move to the next suitable deadline.

## 4. Before resubmitting, answer: new venue or new content?

State which one on the first line of the resubmission plan, with evidence:

- **New content:** map every substantive review comment from the last round to a new experiment, theorem, or control in this round, each with an artifact key.
- **New venue:** explain why the last round's negative comments do not apply at the new venue (different referee pool, different evaluation criteria), and show that the new venue's bar for the same content is not lower.

If you cannot answer, it is an unchanged resubmission. Do not send it. There is no cap on the number of resubmissions, but each one must add content and finish its matrix.

## 5. Execution rules

- Every new check must fail once on purpose when you write it.
- Before reporting "fixed", have an independent pass re-check against current files and report only items it marks RESOLVED.
- Do not launch work on shared GPUs (any card with other people's processes) without an explicit go-ahead from the user. An idle card is not permission.
- Write out the arithmetic for time-zone conversions (AoE is UTC-12) and give deadlines in the user's local time.
- Ask where every number comes from. Without an artifact key, leave the slot empty and say so.
- When the same mistake happens twice, stop writing notes about it. Turn the fix into a script or a safer default. A note prevents one repeat; a script prevents all of them.
