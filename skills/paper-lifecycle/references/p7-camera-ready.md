# P7 Camera-ready

Most examples here come from ACM proceedings (acmart); the checks carry over to other publishers.

## Rights and metadata

- Copy rights, ISBN, and DOI item by item from the rights-review email, not from memory. Match author emails to the rights record character for character. Mark equal contribution with `\authornote`. Upgrade the style file to the required version.
- **When the publisher's preparation page conflicts with the rights email, the system-generated snippet in the email wins.** The snippet is generated from this paper's conference record and matches the digital-library booktitle; the preparation page is generic and can be out of date. Verify hard facts such as the conference ordinal yourself (count from the first edition's year). Diff the snippet against the preamble for every paper; do not copy the string from another paper.
- **You cannot see the rights form after submitting it.** Before uploading, read the review area on the submission page, which shows the title and author data from the publisher's record. A single error in the form (for example a district entered as the city) can be applied to every author. Decide "fix the form or fix the paper" by the facts, not by which came first. Re-filing the form produces a new snippet; diff it against the preamble again.
- Author guideline pages can embed a paper-specific code block (submission ID, received and accepted dates, author block down to city, who is `\correspondingauthor`). Read the raw HTML yourself; summaries drop it. Diff it line by line against the preamble. `\correspondingauthor` means the rights-form contact, which can differ from the academic corresponding author; do not overwrite one with the other.
- Add `\authornote{Corresponding author.}` if your institution counts corresponding authorship. acmart does not require it and the automatic checks do not flag its absence. Adding it changes no names, order, affiliations, or emails, so it creates no discrepancy with the rights record, and it costs no space.

## Page limits and layout

- Refit to the camera-ready page policy (often one extra page). Check for leftover preset values before touching numbers; the camera-ready is the last chance to catch them.
- **De-anonymizing adds length.** The author block, copyright line, and corresponding-author footnote can push the conclusion onto a new page. Check which page the References heading starts on and whether body text precedes it; total page count is not the test. Fix in this order: (1) `\usepackage{microtype}` (often required anyway; it saves lines and often clears overfull boxes); (2) measure white space inside figures with `gs -sDEVICE=bbox` and crop with `trim=...,clip`, then render to confirm nothing was cut; (3) only then edit text. Do not shrink float spacing first: guidelines often forbid changing template formatting and require vertical space around floats.
- **Check that the two columns on the last page are balanced whenever the body length changes.** Only the publisher's upload check tests this; local builds say nothing. Measure the difference between the bottoms of the two columns:
  ```bash
  pdftotext -bbox -f <last> -l <last> main.pdf - \
    | grep -o 'xMin="[0-9.]*"[^>]*yMax="[0-9.]*"'   # split by page midline on xMin; take max yMax per side
  ```
  Observed on US Letter two-column: 22 pt passed, 323 pt was rejected. Fix with `\usepackage{balance}` and a `\balance` before `\bibliographystyle`: no page cost, no content change, no acmart warning. Do not delete text to balance; that can break the page-limit check you just passed.
- After any camera-ready change, even one sentence, re-check column balance and the References start page together before uploading.

## Text fields on the submission page

- Publisher submission pages often ask you to paste Title, Abstract, References, CCS XML, and Keywords in addition to uploading files. Take the abstract from the `.tex`, not the PDF. Keywords may need semicolons even though the PDF uses commas.
- **Flatten references from the `.bbl`, never from the PDF.** `pdftotext` splits entries across lines, and TeX hyphenation cannot be told apart from real hyphens, producing entries such as "misinfor-mation". Expand `\bibinfo{x}{y}` to y, strip wrappers such as `\showarticletitle{}` and `\emph{}`, and spot-check numbering against [1] to [N] in the PDF. Compare the de-macroed abstract against the PDF character by character after normalization.
- If a thumbnail size is recommended, compute its aspect ratio. 302x392 is US Letter, so it wants the first page: render page 1 with `pdftoppm` and resize.

## CCS concepts

- **Check CCS codes against the official data.** Source: `https://dl.acm.org/pb-assets/dl_ccs/acm_ccs2012-1626988337.xml` (the interactive CCS page is JavaScript-only). The `rdf:about` attribute of each `<skos:Concept>` is the full dotted code, so build an `id -> prefLabel` map and match exactly. If you rebuild the hierarchy instead, accumulate all `skos:broader` entries; concepts repeat, and overwriting parents marks valid polyhierarchy codes as wrong. CCS codes in arXiv preprints are unreliable. LLM-generated CCS blocks get codes wrong just as they get bibliography entries wrong.
- The typical error is a whole wrong subtree. A matching root category is not a pass.

## Figures

- **Render every figure and look at it.** Text extraction shows strings but not errors in them: template leftovers, typos, one letter assigned to two modules, subtitles repeated at the bottom of a box, a panel title copied from another panel, edge labels that match none of the legend's names. Render with `pdftoppm -r 300`, crop each figure, read it, and check that labels match the legend and the body terminology. After deleting a duplicated element, delete the separator line it leaves behind.
- **Re-export slide figures with "Export / Save as PDF", not "Print to PDF".** Printing produces A4 instead of the slide size, resamples bitmaps, flattens transparency, and breaks every `trim=` value. To rescue a printed version: the slide sits full-width and centered on A4, so derive the crop box from a full-bleed background with `gs` bbox and re-place it with `\includegraphics[width=<w>bp,viewport=...,clip]`. Two traps: use `bp` (TeX `pt` is 1/72.27 inch, a 0.37% error), and make the wrapper page's `textheight` clearly larger than the figure, or the figure is pushed to page 2 and `\includegraphics` embeds the blank page 1 (a sudden drop in file size is the first sign).

## Pointers to the appendix

- **Before the camera-ready, confirm whether the appendix goes into the digital library.** If the rights form says there is no auxiliary material, every "details in the supplementary" in the body dangles in the published version, possibly under a headline number. Scan with `grep -rniE "supplement|appendix" sections/ main.tex` (the `-i` matters: "Supplementary A.1" is easy to miss), then confirm on the final PDF: `pdftotext main.pdf - | grep -ciE "supplement|appendix"` must be 0.
- Fix in this order: (1) if the text is already self-contained, delete the pointer; (2) if the number fits, inline it with a same-length replacement (one extra line can push References to the next page); (3) if the appendix is truly required, change the auxiliary-material answer and use the portal's supplementary process. Core specifications (a full grammar, for example) tend to hide in the Method section; point to the released code if they cannot be inlined.

## Citations and DOIs

- **Check a "DOI author mismatch" warning against Crossref before editing** (`api.crossref.org/works/<doi>`). It may be real (incomplete author list) or a false positive from a hyphenated surname split across lines and rejoined; pin it with `\nobreakdash`.
- Add missing DOIs only for entries cited as arXiv preprints (verify each title with DataCite). ICLR, NeurIPS, PMLR, and many books have no DOI; residual "no DOI" warnings for them are correct.
- **Crossref `query.bibliographic` returns look-alikes.** A title search can return posted content or an unrelated paper with a similar title. Check the type and the full title; never accept the first hit automatically.

## Sibling papers

- A camera-ready defect confirmed in one paper (CCS code, `\\` in the title leaking into the running head or metadata, venue string, DOI) must be re-checked in sibling papers prepared at the same time, in the same commit. Papers built from the same template share defects.

## Artifacts

- Data availability statements usually need a DOI link (Zenodo, figshare); a GitHub link does not qualify.
- **Two artifact rules:** (1) a DOI only in the text via `\url` does not count; checkers scan the reference list, so create a `@misc` entry for the artifact and `\cite` it; (2) only a version DOI is accepted, not a Zenodo concept DOI. Each new artifact version means a paper edit, so finalize the package before publishing to Zenodo. The DOI in the form and in the references must match exactly. Submit the artifact before uploading the camera-ready, or the paper check compares against the old DOI.

## Publication is not the same as passing checks

- Open-access venues can block publication until the article processing charge is paid. Payment and camera-ready upload do not block each other; do both. The payment link is usually a tokenized, per-paper link sent in the rights thread, not in the author kit; ask for it if missing. After paying, reply to tell the publisher; they may not be notified automatically. Check that the receipt shows this paper's DOI and keep it for reimbursement.

## Records

- File every conference or publisher email the user shares under `<paper repo>/correspondence/`, one file per email (`YYYY-MM-DD-sender-subject.md`: verbatim text, what it means, what to do, draft reply), with an `INDEX.md`. **Gitignore this directory**: author-kit emails contain per-paper authorization tokens. If the original is incomplete, mark it PARTIAL RECORD and quote only what you saw.
- Keep receipts, registration confirmations, and invoices under `<paper repo>/register/` with original file names, also gitignored. Link to them from `correspondence/`; do not store two copies. Do not leave receipts only in a mail client's cache.
- Record registration and travel details (confirmation numbers, hotel, badge affiliation) where the user keeps notes.
