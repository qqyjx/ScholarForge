#!/usr/bin/env python3
"""Provenance audit: every number in a paper is a LaTeX macro tied to a run-artifact key.

Checks, for one .tex file and one macro map:

  MISMATCH   a macro value differs from the artifact value after formatting (round once, from the raw value)
  MISSING    the artifact file or key does not exist, or a mapped macro is not defined in the .tex
  UNMAPPED   a macro with a numeric value has no entry in the map
  HARDCODED  a decimal or percentage appears in the body outside a macro (hard failure)
  UNUSED     a mapped macro is never used in the body (soft advisory)

A line that ends with the comment `% prov:ok` is exempt from HARDCODED.

Map format (macro names have no backslash):
  {"macros": {"accMain": {"artifact": "results/main.json", "key": "metrics.accuracy",
                          "scale": 100, "fmt": ".1f"}}}
The artifact path is relative to the map file. `key` is a dotted path; list items use integer parts.

Usage:
  python -m scholarforge.tools.provenance_audit --tex main.tex --map macros_map.json
  python -m scholarforge.tools.provenance_audit --selftest
Exit status 1 if any hard failure is found. The last output line is RESULT=PASS or RESULT=FAIL.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HARD_KINDS = {"MISMATCH", "MISSING", "UNMAPPED", "HARDCODED"}

DEF_RE = re.compile(r"\\(?:re)?newcommand\*?\{\\(\w+)\}(?:\[\d\])?\{([^{}]*)\}")
NUMERIC_VALUE_RE = re.compile(r"^\s*-?\d+(?:\.\d+)?\s*(?:\\?%)?\s*$")
# Commands whose argument is never a result: references, citations, file names, environments.
ARG_STRIP_RE = re.compile(
    r"\\(?:cite[a-z]*|ref|eqref|cref|autoref|label|url|href|input|include|includegraphics|usepackage|"
    r"documentclass|bibliography|bibliographystyle|begin|end)\*?(?:\[[^\]]*\])*\{[^{}]*\}"
)
DIMENSION_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:\\(?:line|text|column)width|pt|cm|mm|em|ex|in)\b")
NUMBER_RE = re.compile(r"(?<![\w.\\])\d+\.\d+|(?<![\w.\\])\d+(?:\.\d+)?\s*\\?%")


@dataclass
class Finding:
    kind: str
    line: int
    macro: str
    message: str

    @property
    def hard(self) -> bool:
        return self.kind in HARD_KINDS


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    checked: int = 0  # number of mapped macros that were compared with an artifact value

    @property
    def hard_failures(self) -> list[Finding]:
        return [f for f in self.findings if f.hard]

    @property
    def soft_advisories(self) -> list[Finding]:
        return [f for f in self.findings if not f.hard]

    @property
    def ok(self) -> bool:
        return not self.hard_failures


def strip_comment(line: str) -> str:
    """Remove a trailing TeX comment (an unescaped %)."""
    return re.sub(r"(?<!\\)%.*$", "", line)


def parse_macros(tex: str) -> dict[str, tuple[str, int]]:
    """Return {macro name: (value, line number)} for every \\newcommand with a brace-free body."""
    out: dict[str, tuple[str, int]] = {}
    for i, line in enumerate(tex.splitlines(), 1):
        for m in DEF_RE.finditer(strip_comment(line)):
            out[m.group(1)] = (m.group(2).strip(), i)
    return out


def lookup(data: Any, key: str) -> Any:
    """Follow a dotted key path through dicts and lists. Raises KeyError if absent."""
    cur = data
    for part in key.split("."):
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                raise KeyError(key) from None
        elif isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise KeyError(key)
    return cur


def format_value(raw: float, entry: dict) -> str:
    """Scale and format a raw artifact value once. `fmt` is a Python format spec."""
    x = raw * float(entry.get("scale", 1))
    fmt = entry.get("fmt", "")
    return format(int(round(x)) if fmt == "d" else x, fmt)


def body_lines(tex: str) -> list[tuple[int, str]]:
    """Lines between \\begin{document} and \\end{document}, comments removed, macro definitions dropped."""
    lines = tex.splitlines()
    start, end = 0, len(lines)
    for i, line in enumerate(lines):
        if r"\begin{document}" in line:
            start = i + 1
        if r"\end{document}" in line:
            end = i
            break
    out = []
    for i in range(start, end):
        raw = lines[i]
        if "prov:ok" in raw:
            continue
        text = strip_comment(raw)
        if DEF_RE.search(text):
            continue
        out.append((i + 1, text))
    return out


def audit(tex_path: Path, map_path: Path) -> Report:
    tex = Path(tex_path).read_text(encoding="utf-8")
    mapping = json.loads(Path(map_path).read_text(encoding="utf-8")).get("macros", {})
    mapping = {k.lstrip("\\"): v for k, v in mapping.items()}
    root = Path(map_path).parent
    macros = parse_macros(tex)
    rep = Report()
    cache: dict[str, Any] = {}

    for name, entry in mapping.items():
        if name not in macros:
            rep.findings.append(Finding("MISSING", 0, name, f"\\{name} is in the map but not defined in the .tex"))
            continue
        value, line = macros[name]
        art = entry["artifact"]
        try:
            if art not in cache:
                cache[art] = json.loads((root / art).read_text(encoding="utf-8"))
            raw = lookup(cache[art], entry["key"])
            expected = format_value(raw, entry)
        except FileNotFoundError:
            rep.findings.append(Finding("MISSING", line, name, f"\\{name}: artifact {art} not found"))
            continue
        except (KeyError, TypeError, ValueError):
            rep.findings.append(Finding("MISSING", line, name, f"\\{name}: key {entry['key']} not usable in {art}"))
            continue
        rep.checked += 1
        if value.replace("\\%", "").replace("%", "").strip() != expected:
            rep.findings.append(Finding("MISMATCH", line, name,
                                        f"\\{name} = {value} but {art}:{entry['key']} gives {expected}"))

    for name, (value, line) in macros.items():
        if name not in mapping and NUMERIC_VALUE_RE.match(value):
            rep.findings.append(Finding("UNMAPPED", line, name, f"\\{name} = {value} is numeric and has no artifact key"))

    body = body_lines(tex)
    for line_no, text in body:
        cleaned = DIMENSION_RE.sub(" ", ARG_STRIP_RE.sub(" ", text))
        for m in NUMBER_RE.finditer(cleaned):
            rep.findings.append(Finding("HARDCODED", line_no, "", f"hard-coded number {m.group(0).strip()!r}: {text.strip()[:70]}"))

    body_text = "\n".join(t for _, t in body)
    for name in mapping:
        if name in macros and not re.search(r"\\" + re.escape(name) + r"(?![A-Za-z])", body_text):
            rep.findings.append(Finding("UNUSED", macros[name][1], name, f"\\{name} is defined and mapped but never used"))
    rep.findings.sort(key=lambda f: (not f.hard, f.line, f.kind))
    return rep


def render(rep: Report) -> str:
    lines = [f"mapped macros compared with artifacts: {rep.checked}"]
    for f in rep.findings:
        where = f"line {f.line}" if f.line else "map"
        lines.append(f"  [{'FAIL' if f.hard else 'WARN'}] {f.kind:<9} {where:<8} {f.message}")
    lines.append("RESULT=" + ("PASS" if rep.ok else "FAIL"))
    return "\n".join(lines)


def selftest() -> int:
    """Four small papers. The clean one must pass. The other three must each fail."""
    art = {"metrics": {"acc": 0.8137}}
    clean = "\\newcommand{\\acc}{81.4}\n\\begin{document}\nWe get \\acc\\% accuracy.\n\\end{document}\n"
    cases = [
        ("clean", clean, True),
        ("hard-coded", clean.replace("\\acc\\%", "81.4\\%"), False),
        ("mismatch", clean.replace("{81.4}", "{82.0}"), False),
        ("unmapped", clean + "\\newcommand{\\extra}{3.5}\n", False),
    ]
    ok_all = True
    with tempfile.TemporaryDirectory() as t:
        root = Path(t)
        (root / "a.json").write_text(json.dumps(art))
        (root / "map.json").write_text(json.dumps(
            {"macros": {"acc": {"artifact": "a.json", "key": "metrics.acc", "scale": 100, "fmt": ".1f"}}}))
        for name, tex, expect_ok in cases:
            (root / "p.tex").write_text(tex)
            got = audit(root / "p.tex", root / "map.json").ok
            good = got == expect_ok
            ok_all &= good
            print(f"  case {name:<11} expected {'PASS' if expect_ok else 'FAIL'}, got {'PASS' if got else 'FAIL'}"
                  f"  -> {'ok' if good else 'SELFTEST ERROR'}")
    print("selftest", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--tex", type=Path)
    ap.add_argument("--map", type=Path, dest="map_path")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.tex or not a.map_path:
        ap.error("--tex and --map are required")
    rep = audit(a.tex, a.map_path)
    print(render(rep))
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main())
