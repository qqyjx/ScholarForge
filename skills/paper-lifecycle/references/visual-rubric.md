# Visual rubric for figures and tables

Judge every item on the rendered figure (for example `pdftoppm -r 300`), not by reading the source.

## Figures (score each main-text figure per item: PASS / SHOULD / MUST)

- **F1 Form:** chart type fits the task (magnitude: bars or dots; change: lines; distribution: histogram or violin; matrix: heatmap with 7 or fewer levels). No dual y-axes. No pie charts. No value gradients on nominal categories. Split an overloaded single panel into small multiples.
- **F2 Color:** at most 4 categorical colors. The same entity (arm, model, method) has the same color and order across the paper. Validate the palette for color-vision deficiency (adjacent pairs Delta E of 8 or more; the `dataviz` skill's palette validator works if installed). Sequential: one hue, varying lightness. Diverging: two poles with a gray midpoint. Text in ink color, not series color, except for a few direct labels.
- **F3 Marks:** thin lines and small markers. Grid lines solid light gray or none; no dashed grids. Remove top and right spines. Every estimate has an error bar or CI. Do not print a number on every point; label only ends, extremes, or the headline. Two or more series need a legend, and it must not cover data.
- **F4 Type:** every glyph at least 8 pt at print width, measured from the PDF, not from script parameters. One font family across figures, matching the body text. Panel titles state the finding, not the variable name. Axes have units. No clipped or overlapping labels.
- **F5 Layout:** figure width is the text width or 0.48 of it, inserted at natural size without scaling. Reasonable aspect ratio and balanced white space. Multi-panel figures labeled (a), (b), (c) with equal panel heights.
- **F6 Information:** the caption's first sentence is the conclusion. The figure can be read without the body text. Figure 1 shows a phenomenon, not the architecture.
- **F7 Consistency:** one palette, line width, font size, spine style, and marker set across the paper, including the appendix.

## Tables (score each main-text table per item)

- **T1** booktabs (`\toprule`, `\midrule`, `\bottomrule`); no vertical or double lines.
- **T2** Decimal-aligned numbers (siunitx `S` or fixed decimals), one precision per column, one format for plus-minus, CIs, and thousands separators.
- **T3** When comparing, bold the best per column (optionally underline the second) and state the rule in the caption. Explain non-comparable cells (--).
- **T4** Units in column headers; grouped headers with `\cmidrule`; abbreviations expanded in the caption.
- **T5** The caption's first sentence is the conclusion, not "Results on X".
- **T6** Width within the text width, no overfull boxes, font at least 8 pt (`\small` or larger), at most 8 columns (otherwise transpose or split).
- **T7** Row order has a reason (dataset then method, or by headline); groups separated with `\addlinespace`; no columns that repeat a figure.
- **T8** Tables and figures complement each other; each exact value appears once.

## Audit output

One file per paper: a paragraph per figure and table (cropped PNG path, verdict per item, the concrete fix naming the generating script or LaTeX line), a "figure system" section (entity-to-color table, validator output, smallest measured font size), and a fix list sorted MUST before SHOULD. The audit does not edit the paper.
