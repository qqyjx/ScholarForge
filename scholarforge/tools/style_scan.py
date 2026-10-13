#!/usr/bin/env python3
"""Style scan: report filler phrases and other prose tells in LaTeX body text. Reports only; never edits.

Comments, macro definitions, preamble commands and tabular rows are skipped.
Every hit is a soft advisory: a human decides whether to reword.

Usage:
  python -m scholarforge.tools.style_scan PAPER_DIR_OR_TEX [--lines]
  python -m scholarforge.tools.style_scan --selftest
Exit status 1 if there is any hit. The last output line is RESULT=PASS or RESULT=FAIL.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RULES: list[tuple[str, re.Pattern[str]]] = [
    ("dash", re.compile(r"---|\u2014")),
    ("worth-noting", re.compile(r"\bIt is (?:worth noting|important to note|noteworthy)\b", re.I)),
    ("sentence-adverb", re.compile(r"\b(?:Crucially|Notably|Importantly|Interestingly|Remarkably|Strikingly),?")),
    ("stock-verb", re.compile(r"\b(?:delve[sd]?|leverag(?:e|es|ed|ing)|unlock(?:s|ed|ing)?|underscor(?:e|es|ed)|showcas(?:e|es|ed|ing))\b", re.I)),
    ("not-merely", re.compile(r"\bnot\s+(?:merely|just|simply)\b", re.I)),
    ("by-construction", re.compile(r"\bby construction\b", re.I)),
    ("hype-noun", re.compile(r"\b(?:game-chang\w+|groundbreaking|revolutionary|cutting-edge|paradigm shift|holistic|tapestry|realm|landscape)\b", re.I)),
    ("bold-colon", re.compile(r"\\textbf\{[^}]{2,40}\}:")),
]
SKIP_LINE = re.compile(r"^\s*(%|\\(?:newcommand|renewcommand|providecommand|def|usepackage|documentclass|bibliography))")
TABLE_ROW = re.compile(r"&|\\\\\s*$")


def scan_text(text: str) -> list[tuple[int, str, str]]:
    """Return (line number, rule name, line excerpt) for every hit."""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if SKIP_LINE.match(line):
            continue
        body = re.sub(r"(?<!\\)%.*$", "", line)
        tabular = bool(TABLE_ROW.search(body))
        for name, rx in RULES:
            if tabular and name == "dash":
                continue
            for _ in rx.finditer(body):
                hits.append((i, name, line.strip()[:90]))
    return hits


def tex_files(target: Path) -> list[Path]:
    return [target] if target.is_file() else sorted(target.rglob("*.tex"))


def scan_path(target: Path) -> dict[Path, list[tuple[int, str, str]]]:
    return {f: scan_text(f.read_text(encoding="utf-8", errors="ignore")) for f in tex_files(target)}


def render(result: dict[Path, list[tuple[int, str, str]]], lines: bool = True) -> str:
    out, total = [], 0
    for f, hits in result.items():
        counts: dict[str, int] = {}
        for _, name, _ in hits:
            counts[name] = counts.get(name, 0) + 1
        total += len(hits)
        out.append(f"{f.name}: {len(hits)} hits  " + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
        if lines:
            out += [f"  [WARN] line {n:<3} {name:<16} {ex}" for n, name, ex in hits]
    out.append("RESULT=" + ("FAIL" if total else "PASS"))
    return "\n".join(out)


def selftest() -> int:
    """A clean sentence must give 0 hits. A planted filler sentence must give hits."""
    clean = "We measure accuracy on two systems and report the difference.\n"
    dirty = "It is worth noting that we leverage a model --- crucially, it works.\n"
    n_clean, n_dirty = len(scan_text(clean)), len(scan_text(dirty))
    ok = n_clean == 0 and n_dirty >= 3
    print(f"  clean sentence: {n_clean} hits (expect 0)")
    print(f"  filler sentence: {n_dirty} hits (expect at least 3)")
    print("selftest", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("target", nargs="?", type=Path)
    ap.add_argument("--lines", action="store_true", help="list every hit")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.target:
        ap.error("a .tex file or a directory is required")
    res = scan_path(a.target)
    print(render(res, lines=a.lines))
    return 1 if any(res.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
