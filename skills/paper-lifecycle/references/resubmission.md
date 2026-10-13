# Resubmission

## The pipeline syncs numbers, not warnings

When a paper moves to a new venue, the new repository is usually a copy of the original at some commit. Findings made in the original after that commit do not follow automatically. The dangerous case: a result is withdrawn in the original venue's public review thread, while the same claim is still under review at the new venue. Public review threads are searchable, and being found out is far worse than disclosing.

Mechanisms to guard against:

1. **The new repository is a snapshot.** Record the base commit when creating it. Before submitting, read the original's history since that commit (`git log <base>..HEAD`), especially the review directory.
2. **Sync contracts cover numbers, not prose.** A contract that copies `results_*` into the paper will never carry a finding that invalidates a result if that finding lives in a review response or author response post. Include the original's review and author response material in the sync contract explicitly.
3. **An original under review is the high-risk period**, because review is when defects surface. While the original is in review, read its full review thread the day before submitting the new version and ask of each item: which number or sentence in this paper does it affect?

**Three questions in the last minute before a resubmission** (run alongside P4):

- What is the original paper's current review status? Has anything been conceded, withdrawn, or promised?
- Does this paper's headline sentence still hold in the original's public thread?
- Does any commit in the original since the base mention audit, correction, or withdrawal?

If it happens anyway, do not wait for the decision. There are two options: withdraw, or disclose to the program chairs or area chair.

**First question for any resubmission: new venue or new content?** Write the answer on the first line of the resubmission plan with evidence. See [submission gate](submission-gate.md) section 4.

## Converting a NeurIPS single-column paper to AAAI two-column

1. Copy the preamble from a previous successful conversion. The AAAI style forbids `wrapfig` and `hyperref`.
2. Check every figure. A single-column `figure` at `\textwidth` overlaps the other column in two-column layout. Make spanning figures `figure*` (declare them where the style allows; declaring `figure*` on the first page, or loading `tikz` in `main`, can push content into the margins) and set in-column figures to `\columnwidth`.
3. Unbreakable inline material (math-mode enumerations, long `\texttt` strings) must become text mode. Split long single-line equations with `aligned`. Replace oversized `\left|...\right|` with `\bigl|`.
4. If the supplementary compiles separately, pin the appendix letters referenced from the main text (`\ref{app:*}`) to the supplementary's section order. Change both together. Do not leave references to floats inside the appendix.
5. Scan the code package for the four anonymity categories and also for traces of the previous venue: its name, handoff scripts, auto-push hooks with a GitHub remote, "host" fields in manifest JSON, and time-zone or location hints. Drop operational helper scripts (watchers, dispatchers, schedulers).
6. "Deferred to camera-ready" statements tend to repeat in several places. When trimming pages, remove the repeats first.
