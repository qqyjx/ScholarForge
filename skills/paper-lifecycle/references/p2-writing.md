# P2 Writing

- Open the experiments section with RQ1 to RQn, not with a system description.
- **No mannered prose.** This applies to every text: main body, appendix, author response, emails to chairs and editors, form statements, replies to the user, commit messages, and code comments. Write it this way in the first draft, then do one separate pass before finalizing that changes only wording. Keep that pass apart from page trimming, number audits, and anonymity scans, and do not touch numbers or claims in it.
  - Mannered prose uses metaphor and flourish where a literal statement exists: "this knob is where the action is" instead of "this parameter has the largest effect". It is imprecise because metaphors carry connotations the writer did not choose, and it makes the reader work harder. When a literal phrase is available, use it.
  - Keep sentences short, one idea each. Split paragraphs by idea. Remove repetition and transitions that add no information.
- **Paraphrase sources in your own words.** In related work and discussion, put any phrase taken from the original in quotation marks. Do not restate a source's paragraphs.
- **The main text holds the evidence.** Headline numbers, significance, and measured values for assumptions all go in the main text (table columns or inline). The appendix holds proofs, protocol details, hyperparameters, and reproduction material, designed so a referee who skips it loses nothing. No promises in the appendix ("the table will be generated") without the table.
- Style limits: no bullet lists in the main body; at most two parentheses per paragraph; `\paragraph{}` instead of subsubsections; abstract, contribution list, and conclusion in the same order; 2 or 3 limitations that do not undercut the paper.
- Page strategy: draft at the target length minus half a page to leave room for figures and tables. Trimming cuts wording, never evidence. If word cuts shorten a paragraph's last line without removing it, use a stronger lever (figure width, result-figure height, table notes). `\looseness=-1` is a legitimate tool.

## LLM prose tells referees name

Scan for these in the style pass. Count each per 1000 words; more than 2 of any one means rewrite.

1. Long negative parallelisms: "not X, but Y".
2. Non-human subjects with active verbs: "the paper surfaces", "the table spends", "the method headlines".
3. "By construction", "exactly the", "precisely".
4. High em-dash density.
5. Blurred agency: if the training harness decides, do not write "the policy decides".
6. Emphasis on details nobody would stress, such as "on real GPUs" followed by a list of everything not simulated.

## Terms and headline sentences

- Define every term before its first use. One word, one meaning throughout. Section 6.1 must not rely on an object introduced in 6.3. The main algorithm belongs in the main text.
- Check every headline sentence against your own tables. "Same abstention" when F1 differs by 0.04, "consistent improvements" when one cell is worse, "an order of magnitude" for a 3.8x gap, a percentage that cannot arise from 30 binary runs: automated referees catch these, and they cost nothing to fix before submission.
