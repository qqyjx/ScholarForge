"""A mock submit-gate for the toy paper, built on the orchestrator.

It mirrors `workflows/submit-gate.js`: a precheck, then parallel gates, then a compliance matrix.
The gates are the local tools in `scholarforge.tools`. There is no model call.

Gate           Tool                      Hard or soft
provenance     provenance_audit          hard (MISMATCH, MISSING, UNMAPPED, HARDCODED); UNUSED is soft
style          style_scan                soft
layout         page_sweep (estimate)     hard
anon           forbidden-string search   hard
"""
from __future__ import annotations

import re
from pathlib import Path

from . import orchestrator as orch
from .tools import page_sweep, provenance_audit, style_scan

GATE_ORDER = ("provenance", "style", "layout", "anon")


def precheck(paper_dir: str) -> dict:
    """Locate main.tex and the macro map. `toplevel` is what the guard compares with the expected path."""
    root = Path(paper_dir).resolve()
    main, mp = root / "main.tex", root / "macros_map.json"
    notes = [f"missing {p.name}" for p in (main, mp) if not p.exists()]
    return {"ok": not notes, "toplevel": str(root), "main_tex": str(main), "map": str(mp), "notes": notes}


def _result(gate: str, hard: list[str], soft: list[str], evidence: list[str]) -> dict:
    verdict = "FAIL" if hard else ("WARN" if soft else "PASS")
    return {"gate": gate, "verdict": verdict, "hard_failures": hard, "soft_advisories": soft, "evidence": evidence}


def gate_provenance(pre: dict) -> dict:
    rep = provenance_audit.audit(Path(pre["main_tex"]), Path(pre["map"]))
    fmt = lambda f: f"{f.kind} line {f.line}: {f.message}"
    return _result("provenance", [fmt(f) for f in rep.hard_failures], [fmt(f) for f in rep.soft_advisories],
                   [f"{rep.checked} mapped macros compared with artifacts"])


def gate_style(pre: dict) -> dict:
    hits = style_scan.scan_text(Path(pre["main_tex"]).read_text(encoding="utf-8"))
    return _result("style", [], [f"line {n} {name}: {ex}" for n, name, ex in hits], [f"{len(hits)} style hits"])


def gate_layout(pre: dict, limit: float, words_per_page: int = 600) -> dict:
    pages = page_sweep.estimate_pages(Path(pre["main_tex"]), words_per_page)
    hard = [f"estimated {pages:.2f} pages, limit {limit:g}"] if pages > limit else []
    return _result("layout", hard, [], [f"estimated {pages:.2f} pages (limit {limit:g})"])


def gate_anon(pre: dict, forbidden: list[str]) -> dict:
    text = Path(pre["main_tex"]).read_text(encoding="utf-8")
    hard = [f"line {i}: contains {s!r}" for i, line in enumerate(text.splitlines(), 1)
            for s in forbidden if re.search(re.escape(s), line, re.I)]
    return _result("anon", hard, [], [f"searched for {len(forbidden)} forbidden strings"])


def run_gate(paper_dirs: list[str], page_limit: float = 1.0, forbidden: list[str] | None = None,
             limit: int = 3) -> tuple[list[dict], orch.Trace]:
    """Run the mock submit-gate on each paper directory. Returns the compliance rows and the trace."""
    forbidden = forbidden if forbidden is not None else ["Jane Doe", "toy-lab"]
    trace = orch.Trace()
    trace.phase("Precheck", "paper directory, main.tex, macro map")
    mk = lambda label, fn: orch.Agent(label, fn, tier="mechanical", phase="Gates", schema=orch.validate_gate)

    def gates(pre: dict, item: str) -> list[orch.Agent]:
        name = Path(item).name
        return [
            mk(f"provenance:{name}", lambda: gate_provenance(pre)),
            mk(f"style:{name}", lambda: gate_style(pre)),
            mk(f"layout:{name}", lambda: gate_layout(pre, page_limit)),
            mk(f"anon:{name}", lambda: gate_anon(pre, forbidden)),
        ]

    trace.phase("Gates", f"{len(GATE_ORDER)} checks per paper, at most {limit} at once")
    rows = orch.pipeline([str(Path(p).resolve()) for p in paper_dirs], precheck, gates, trace, limit)
    return orch.compliance(rows), trace


def render_matrix(rows: list[dict]) -> str:
    """Compliance matrix: one row per paper, one column per gate."""
    head = f"{'paper':<20}" + "".join(f"{g:<13}" for g in GATE_ORDER) + "verdict"
    out = [head, "-" * len(head)]
    for r in rows:
        by = {g["gate"]: g["verdict"] for g in r["gates"]}
        out.append(f"{Path(r['item']).name:<20}" + "".join(f"{by.get(g, '-'):<13}" for g in GATE_ORDER) + r["verdict"])
    return "\n".join(out)


def render_details(rows: list[dict]) -> str:
    out = []
    for r in rows:
        for g in r["gates"]:
            for h in g["hard_failures"]:
                out.append(f"  [FAIL] {g['gate']:<11} {h}")
            for s in g["soft_advisories"]:
                out.append(f"  [WARN] {g['gate']:<11} {s}")
    return "\n".join(out)
