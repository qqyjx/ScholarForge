# P3 Figures and tables

**Target:** every mechanism is drawn, not only described. Check each figure and table against the [visual rubric](visual-rubric.md). Floor: 5 or more main-text figures, 3 or more tables, and an analysis section ([top-venue bar](top-venue-bar.md) section 4).

## Order of work

1. **Inventory** (read-only): existing figures and tables with page numbers checked against the PDF, mechanisms explained only in text, available page slack, material that could be moved (never significant results), and the top three candidates with their line cost.
2. **Specify and draw:** Figure 1 shows the phenomenon or headline; the architecture figure goes in the method section. For each figure, ask what the reader should see in 5 seconds. Numbers come only from macros or artifacts. Schematics carry no numbers.
3. **Pay for space.** A new figure costs about (figure height in pt + caption lines x 11 + 21) / 11 lines. Deleted words convert to space at about 0.6, and float costs do not add up linearly. Levers, in order: remove paragraphs duplicated in the appendix; compress related work to citation lists (keep every key); remove numbers from captions that the figure already prints; reduce `\textfloatsep`, `\abovecaptionskip`, `\floatsep` (often worth 5-7 lines); reduce existing figure heights. If it still does not fit, move the figure to the appendix with a forward reference. Never delete evidence. Re-run the page probe after every change; do not estimate from word counts.
4. **Visual audit** (read-only) -> fix -> audit again.

## Build chain

- **Schematics:** standalone TikZ -> PDF -> `\includegraphics` at natural size. Build twice independently and compare bytes; check CreationDate and Author; check font embedding. Record the source hash in a provenance file.
- **Data figures:** a shared figure module in the repository (`CreationDate: None`, input hashes in a sidecar or `/Subject`, two runs give the same hash). Register new figures with the repository's figure gate.
- **TikZ has its own gate.** Standalone figures sit outside the matplotlib gate. Give them a byte gate (two builds, same sha256, no CreationDate/ModDate/Author) before installing them, or a stale build ships with the paper.
- **Standalone figures can read macros** via `\input{../../results/macros.tex}`, so their numbers stay in sync with results.
- **Font sizes:** in the ICLR template `\footnotesize` is 9 pt and `\scriptsize` is 7 pt. For inline TikZ use `\fontsize{8pt}{9.5pt}\selectfont`. Measure width before inserting (`\sbox` then `\typeout{\the\wd\box}`); it must be below `\textwidth`.
- **Minimum glyph size:** every glyph at least 8 pt at print width, measured from PDF text spans (PyMuPDF), including subscripts, superscripts, and primes. mathtext roots and subscripts print at 5-5.6 pt; write "sqrt(n)" or use a family name instead. In standalone TikZ, `\DeclareMathSizes{8}{8}{8}{6}` lifts first-level subscripts to 8 pt. Avoid sub- and superscripts in 8 pt schematics; define the symbol in the caption instead.
- **The 8 pt guard must run.** Read span sizes from the final PDF; exit non-zero if the minimum is below 8. Plant a 5 pt label once to prove it fails.
- **Canvas = print width.** `bbox_inches="tight"` crops the canvas, `width=\linewidth` then scales it up, and font sizes and line widths drift by the scale factor. Set `figsize` width to the include width and save without cropping.
- pdftex takes the figure width from the MediaBox, about 1.5 pt wider than `pdfinfo` reports. Read the MediaBox with PyMuPDF in the width gate and leave 1 pt margin.
- Small pgfplots figures need `scale only axis`, or the default margins take half the height.
- **Fonts:** OTF fonts embedded with `pdf.fonttype 42` make poppler warn "Mismatch between font type and embedded font file" on every page with a figure. For clean output use TrueType (for example Liberation Serif/Sans registered with `font_manager.addfont`) and point mathtext `custom` at the same family.
- **Color:** validate the palette for color-vision deficiency before use. Adjacent pairs with low contrast (Delta E 6-8) need direct labels. One entity keeps one color and one position across the paper. Methods, arms, and scales use one neutral family (ink, gray, light gray, filled/hollow/hatched); reserve hue for one kind of entity (datasets or signal families). Ordered quantities use one hue in three steps. Put shared entity colors in one palette module. No dual y-axes, no pie charts, no value gradients on nominal categories.
- **Figures from outside** (exported slides and the like): compare hashes, check DPI of 300 or more with `pdfimages -list`, strip `/Author` and XMP with pikepdf, proofread every label, check symbols against the equations.
- Figure 1 on page 1 with `[t]` can print above the title. Use `[!b]`.

## Tables

booktabs rules, no vertical lines. Align numbers on the decimal point (siunitx `S` columns or a fixed number of decimals), with one precision per column and one format for plus-minus and CIs. When comparing, bold the best value per column and state the rule in the caption. Units in column headers; group headers with `\cmidrule`. The caption's first sentence is the conclusion. Width at most the text width, no overfull boxes, font at least 8 pt, at most 8 columns (otherwise transpose or split). Row order has a reason; group with `\addlinespace`. Tables and figures complement each other; each exact value appears once.

- A fixed-width plus-minus cell (same width as "±10.0") aligns decimals in right-aligned or centered columns without siunitx. Emit negative numbers as `$-$` in the generator. Dagger marks can be zero-width (`\rlap`) so they do not break alignment.

## Layout lessons

- Before drawing, list what each existing figure already shows (grep captions and `fig:` references). A new panel can duplicate an existing one.
- Extending an existing float is cheaper than adding one: it saves a caption header and a `\textfloatsep`, and keeps the float count and page positions. It still triggers reflow, so re-measure.
- With `\widowpenalty=\clubpenalty=10000`, a 4-line paragraph can only split 2+2. When the last page has less than 2 lines plus parskip of slack, the whole paragraph jumps. Test by hiding the last paragraph with `\iffalse...\fi`, then cut whole lines on the last two pages.
- New paragraphs are paid for in lines and only on the last two pages. Cuts on earlier pages get absorbed by floats. Cut transition and restatement sentences on the last two pages first, then compress the new paragraph. Cut sentences with a whitespace-insensitive, unique-match script, then check for leftover seams such as empty `\emph{}` or stray punctuation.
- Order of cuts: sentences said twice (conclusion restating results, method previewing analysis numbers, appendix protocol details repeated in the body), then related work (assert that the set of citation keys is unchanged), then captions. Numbers and claims do not change.
- Changing a caption's first sentence into a conclusion costs lines. Count each caption's lines before and after (`pdftotext -bbox-layout`); cut back within the same caption.
- After any trim, run the repository's number and claim gates and its full test suite. If a guarded sentence was removed, restore it and pay for space elsewhere. Do not edit the guard.
- When a legend covers data, label lines directly with leader lines into an empty corner (order labels by target y, no crossing leaders), or put the legend outside the axes. When all four corners are taken, hang the legend below the panel and clear the x label first.
- Two nearly concentric points cannot be moved: draw the later one smaller with a white ring on top and say so in the caption. The overlap is often the finding.
- Filter placeholder points (coverage=0, n=0) from analysis artifacts before plotting, or the steepest segment in the figure is an artifact.
- Check label collisions mechanically (text bboxes against drawn segments with PyMuPDF). Exclude light grid lines and hatching first, or everything is a false positive.
- Always run `latexmk` as `cd <repo>/paper && latexmk ...`. The working directory drifts between shell calls, and a build from the wrong directory leaves stray `main.*` files while `main.pdf` does not update.
- A probe that reports "body ends on page N+1" means the body has spilled; its pt value is meaningless. Measure the overflow by counting body lines on that page with `pdftotext -layout`, or bisect with a negative `\vbox to -Xpt{}` placed before the conclusion.
