#!/usr/bin/env python3
"""Page-budget sweep: does the body fit the page limit?

Two modes:
  --pdf FILE  count pages with pdfinfo (or, if it is not installed, by counting /Type /Page objects)
  --tex FILE  estimate pages from the word count of the body, for use before a PDF exists

The estimate is a rough guide: words_per_page depends on the template. Use --pdf for a real verdict.
Only text before \\bibliography, \\appendix or \\end{document} counts toward the body.

Usage:
  python -m scholarforge.tools.page_sweep --tex main.tex --limit 8 [--words-per-page 600]
  python -m scholarforge.tools.page_sweep --pdf main.pdf --limit 8
  python -m scholarforge.tools.page_sweep --selftest
Exit status 1 on overflow. The last output line is RESULT=PASS or RESULT=FAIL.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

STOP_RE = re.compile(r"\\(?:bibliography\b|appendix\b|end\{document\})")


def body_words(tex: str) -> int:
    """Count words in the body: drop comments, preamble, commands with short arguments and math."""
    start = tex.find(r"\begin{document}")
    tex = tex[start:] if start >= 0 else tex
    m = STOP_RE.search(tex)
    tex = tex[: m.start()] if m else tex
    tex = re.sub(r"(?<!\\)%.*$", "", tex, flags=re.M)
    tex = re.sub(r"\$[^$]*\$", " ", tex)
    tex = re.sub(r"\\(?:label|ref|cite[a-z]*|includegraphics|begin|end)\*?(?:\[[^\]]*\])*\{[^{}]*\}", " ", tex)
    tex = re.sub(r"\\[A-Za-z]+\*?", " ", tex)
    return len(re.findall(r"[A-Za-z][A-Za-z'-]*|\d+(?:\.\d+)?", tex))


def estimate_pages(tex_path: Path, words_per_page: int = 600) -> float:
    return body_words(Path(tex_path).read_text(encoding="utf-8", errors="ignore")) / words_per_page


def count_pdf_pages(pdf: Path) -> int:
    if shutil.which("pdfinfo"):
        out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        m = re.search(r"^Pages:\s+(\d+)", out, re.M)
        if m:
            return int(m.group(1))
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", Path(pdf).read_bytes()))


def selftest() -> int:
    """A short body must fit one page. A body of 1500 words must overflow a one-page limit."""
    with tempfile.TemporaryDirectory() as t:
        short, long_ = Path(t) / "short.tex", Path(t) / "long.tex"
        short.write_text("\\begin{document}\n" + "word " * 100 + "\n\\end{document}\n")
        long_.write_text("\\begin{document}\n" + "word " * 1500 + "\n\\end{document}\n")
        a, b = estimate_pages(short), estimate_pages(long_)
    ok = a <= 1 < b
    print(f"  short body: {a:.2f} pages (limit 1 -> fits)")
    print(f"  long body:  {b:.2f} pages (limit 1 -> overflow)")
    print("selftest", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tex", type=Path)
    ap.add_argument("--pdf", type=Path)
    ap.add_argument("--limit", type=float, default=8)
    ap.add_argument("--words-per-page", type=int, default=600)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.pdf:
        n, kind = count_pdf_pages(a.pdf), "pages (pdf)"
    elif a.tex:
        n, kind = estimate_pages(a.tex, a.words_per_page), "pages (estimate from words)"
    else:
        ap.error("--tex or --pdf is required")
    over = n > a.limit
    print(f"{n:.2f} {kind}, limit {a.limit:g}: {'OVERFLOW' if over else 'ok'}")
    print("RESULT=" + ("FAIL" if over else "PASS"))
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
