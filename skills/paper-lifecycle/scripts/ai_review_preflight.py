#!/usr/bin/env python3
"""Automated-review rehearsal: mechanical checks for problems that automated AI reviews and
human referees commonly flag (see references/rejection-patterns.md).

Usage: ai_review_preflight.py <paper_dir> [--bib FILE] [--year YYYY]
Scans every .tex under <paper_dir> (recursively; skips files whose name contains 'supp' or
'appendix' for the abstract/number checks but not for text checks). Exit 1 on any FAIL.

Checks
  F1 planned-experiment sentences        (rejection pattern 9)
  F2 LLM prose tells, six patterns       (pattern 6)  — FAIL above threshold, else WARN
  F3 blanket superlatives                (pattern 8)
  F4 abstract numbers absent elsewhere   (pattern 8: headline contradicted / unsourced)
  F5 no seed / spread reporting          (pattern 4)
  F6 bib recency: too few last-2-year refs (pattern 7)
  F7 placeholders TBD/TODO/XXX left in the text
  W1 assumption environments without a measurement pointer (pattern 2)
  W2 acronyms used but never defined     (pattern 10)
"""
import re, sys, os, glob, datetime, argparse

ap = argparse.ArgumentParser()
ap.add_argument('paper_dir')
ap.add_argument('--bib', default=None)
ap.add_argument('--year', type=int, default=datetime.date.today().year)
ap.add_argument('--tell-fail', type=float, default=3.0, help='LLM tells per 1000 words → FAIL')
a = ap.parse_args()

texs = [p for p in glob.glob(os.path.join(a.paper_dir, '**', '*.tex'), recursive=True)
        if '/template/' not in p and 'checklist' not in p.lower()]
if not texs:
    print('no .tex found'); sys.exit(2)

def strip(s):
    s = re.sub(r'(?m)(?<!\\)%.*$', '', s)
    s = re.sub(r'\\(cite[pt]?|ref|label|eqref|autoref|Cref|cref)\{[^}]*\}', '', s)
    return s

body = {p: strip(open(p, errors='ignore').read()) for p in texs}
main_texts = {p: t for p, t in body.items() if not re.search(r'supp|appendix', os.path.basename(p), re.I)}
alltext = '\n'.join(body.values())
maintext = '\n'.join(main_texts.values())
words = max(1, len(re.findall(r'[A-Za-z]+', maintext)))
fails, warns = [], []

def where(pat, text_by_file, flags=re.I):
    out = []
    for p, t in text_by_file.items():
        for m in re.finditer(pat, t, flags):
            line = t.count('\n', 0, m.start()) + 1
            out.append(f"{os.path.relpath(p, a.paper_dir)}:{line}: {m.group(0)[:90].strip()}")
    return out

# F1 planned experiments
pat = r'(queued for (the )?camera[- ]ready|will be (added|run|included|reported)|we plan to|in a future (version|revision)|to be run|sweep (is )?planned|\bNext:|left for the camera|are (being|currently) (run|computed)|results (are )?pending|forthcoming)'
h = where(pat, body)
if h: fails.append(('F1 planned-experiment sentences (delete or run them)', h))

# F2 LLM tells
tells = {
 'negative parallelism "not X, but Y"': r'\bnot (?:only |merely |just |simply )?[^.;:]{3,60}, but (?:rather |instead )?',
 '"by construction"': r'\bby construction\b',
 '"exactly the"': r'\bexactly the\b',
 'em-dash': r'---|—',
 'emphatic "real"/"genuine"/"actual"': r'\b(real|genuine|actual)\s+(GPUs?|hardware|data|deployments?|systems?|users?)\b',
 'filler adverbs': r'\b(crucially|notably|importantly|interestingly|remarkably|it is worth noting|delve)\b',
}
tell_hits = {k: where(v, main_texts) for k, v in tells.items()}
dash = len(tell_hits['em-dash'])
total = sum(len(v) for k, v in tell_hits.items() if k != 'em-dash')
rate = 1000.0 * total / words; dash_rate = 1000.0 * dash / words
summary = [f"{k}: {len(v)}" for k, v in tell_hits.items()] + [f"non-dash tells {total} in {words} words = {rate:.1f}/1000; em-dash {dash_rate:.1f}/1000"]
examples = [x for k, v in tell_hits.items() if k != 'em-dash' for x in v[:3]]
if rate > a.tell_fail: fails.append((f'F2 LLM prose tells {rate:.1f}/1000 words (> {a.tell_fail})', summary + examples))
elif total: warns.append((f'F2 LLM prose tells {rate:.1f}/1000 words', summary + examples))
if dash_rate > 2.0: warns.append((f'F2 em-dash density {dash_rate:.1f}/1000 words (referees list dash density as an LLM tell; convert most to commas or full stops)', tell_hits['em-dash'][:6]))

# F7 placeholders left in the manuscript (referees flag leftover "TBD" and similar)
h = where(r'\b(TBD|TODO|XXX|FIXME|PLACEHOLDER|\?\?\?)\b', {p: t for p, t in main_texts.items() if not re.search(r'/fig', p)}, 0)
if h: fails.append(('F7 placeholders in the manuscript', h))

# F3 blanket superlatives
h = where(r'(surpass(es|ing)? (every|all)|outperform(s|ing)? (every|all)|beats? (every|all)|(every|all) (classic |prior |existing )?(baselines?|methods?) (on|across) (every|all)|best of any method)', main_texts)
if h: fails.append(('F3 blanket superlatives (each must hold in every table cell, else rewrite)', h))

# F4 abstract numbers
abs_m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', alltext, re.S)
abs_src = None
for p, t in body.items():
    if 'abstract' in os.path.basename(p).lower(): abs_src = t
if abs_src and (not abs_m or re.search(r'\\input\{', abs_m.group(1))): abs_txt = abs_src
elif abs_m: abs_txt = abs_m.group(1)
else: abs_txt = ''
if abs_txt:
    rest = alltext.replace(abs_txt, '')
    macro_files = glob.glob(os.path.join(a.paper_dir, '**', '*macros*.tex'), recursive=True) + glob.glob(os.path.join(a.paper_dir, '**', 'results', '*.tex'), recursive=True)
    rest += '\n'.join(open(m, errors='ignore').read() for m in macro_files)
    nums = set(re.findall(r'(?<![\w.])\d+(?:\.\d+)?(?=\s*(?:\\%|%|\b))', abs_txt))
    nums = {n for n in nums if not re.fullmatch(r'(19|20)\d\d', n) and n not in {'1','2','3','4','5','6','7','8','9','10'}}
    missing = [n for n in sorted(nums) if not re.search(r'(?<![\w.])' + re.escape(n) + r'(?![\w])', rest)]
    if missing: fails.append(('F4 abstract numbers found nowhere else in the paper or macros (source each)', missing))
    if not nums and not re.search(r'\\res[A-Za-z]+', abs_txt): warns.append(('F4 abstract has no numbers and no result macros', []))

# F5 seeds / spread
if not re.search(r'\bseeds?\b', maintext, re.I): fails.append(('F5 no "seed" anywhere in the main text', []))
if not re.search(r'(\\pm|±|std\b|standard deviation|confidence interval|\bCI\b)', maintext): fails.append(('F5 no ± / std / CI in the main text', []))
if re.search(r'\bp\s*[<=]\s*0?\.\d', maintext) and not re.search(r'\bpaired\b|permutation|bootstrap|McNemar|Wilcoxon|clustered', maintext, re.I):
    warns.append(('F5 p-values reported but no test named (paired/permutation/bootstrap/McNemar/Wilcoxon/clustered)', []))

# F6 bib recency
bibs = [a.bib] if a.bib else glob.glob(os.path.join(a.paper_dir, '**', '*.bib'), recursive=True)
recent = 0; nbib = 0
for b in bibs:
    s = open(b, errors='ignore').read()
    nbib += len(re.findall(r'@\w+\s*\{', s))
    recent += len(re.findall(r'year\s*=\s*[{"]?\s*(%d|%d)' % (a.year, a.year - 1), s))
if bibs and recent < 5: fails.append((f'F6 only {recent} refs from {a.year-1}-{a.year} out of {nbib} (automated reviews often list 2-5 missing nearest neighbours per paper)', bibs))
elif bibs: warns.append((f'F6 bib recency ok: {recent}/{nbib} from {a.year-1}-{a.year}', []))

# W1 assumptions without measurement pointer
for p, t in body.items():
    for m in re.finditer(r'\\begin\{(assumption|assump)\}(.*?)\\end\{\1\}', t, re.S):
        tail = t[m.end(): m.end() + 1500]
        if not re.search(r'(measur|empiric|Table|Figure|Fig\.|verified|we check|estimate)', m.group(2) + tail, re.I):
            warns.append((f'W1 assumption without a measurement pointer within 1500 chars: {os.path.relpath(p, a.paper_dir)}', [m.group(2)[:100].strip()]))

# W2 undefined acronyms
defined = set(re.findall(r'\(([A-Z][A-Za-z]{1,6})\)', maintext)) | set(re.findall(r'\\newcommand\{\\(\w+)\}', alltext))
used = {}
for w in re.findall(r'\b[A-Z]{2,6}\b', maintext):
    used[w] = used.get(w, 0) + 1
common = {'LLM','LLMS','GPU','GPUS','CPU','RL','AI','ML','NLP','API','URL','USA','AND','OR','NOT','THE','II','III','IV','ACL','ICML','AAAI','NEURIPS','ICLR','CVPR','SOTA','PDF','JSON','CSV','ID','IDS','TV','CI','MIT','BSD','TL','DR','RQ','RQS','SC','QA','VQA','OK','SFT','DPO','PPO','GRPO','LORA','TP'}
undef = sorted(w for w, c in used.items() if c >= 3 and w not in defined and w not in common and not re.search(r'\b' + w + r'\b\s*\(', maintext) and not re.search(r'\(\s*' + w + r'\s*\)', maintext))
if undef: warns.append(('W2 acronyms used ≥3 times and never defined as "(ABC)" (heuristic)', undef[:25]))

for title, items in warns:
    print('WARN', title); [print('   ', x) for x in items[:12]]
for title, items in fails:
    print('FAIL', title); [print('   ', x) for x in items[:12]]
print(f"\n{len(fails)} FAIL, {len(warns)} WARN — {a.paper_dir}")
sys.exit(1 if fails else 0)
