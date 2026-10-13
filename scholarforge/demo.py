"""Offline demo: `python -m scholarforge.demo`.

Runs on the synthetic toy paper in examples/toy-paper/. No network, no model call, no API key.

  1. provenance check: every number macro resolves to an artifact value; a planted hard-coded number is flagged
  2. style scan: planted filler phrases are flagged
  3. mock submit-gate: the checks run through the orchestrator and print a compliance matrix
  4. control run: a repaired copy of the toy paper passes every gate, so the checks are not vacuous

All numbers printed here are computed on the synthetic toy inputs. They are not results of any paper.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

from . import submit_gate
from .tools import provenance_audit, style_scan

DEFAULT_PAPER = Path(__file__).resolve().parent.parent / "examples" / "toy-paper"


def repair(paper: Path) -> None:
    """Fix the planted problems in a copy of the toy paper. Used for the control run only."""
    tex = paper / "main.tex"
    t = tex.read_text(encoding="utf-8")
    t = t.replace("{73.9}", "{74.2}")                                           # stale macro
    t = t.replace("reaches 79.5\\% on the held-out split", "reaches \\accMain\\% on the held-out split")
    t = t.replace("It is worth noting that this paper is a placeholder. We delve into a toy task\nand leverage a toy model to unlock a toy result.",
                  "This paper is a placeholder. It uses a toy task and a toy model.")
    t = t.replace("Crucially, it exists", "It exists").replace(" --- in a toy world", " in a toy world")
    t = re.sub(r"^\\newcommand\{\\nExamples\}.*\n", "", t, flags=re.M)
    tex.write_text(t, encoding="utf-8")
    mp = paper / "macros_map.json"
    mp.write_text("\n".join(l for l in mp.read_text(encoding="utf-8").splitlines() if "nExamples" not in l)
                  .replace('"fmt": "d"},\n  }', '"fmt": "d"}\n  }'), encoding="utf-8")


def section(n: int, title: str) -> None:
    print(f"\n[{n}] {title}\n" + "-" * (len(title) + 5))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="ScholarForge offline demo on a synthetic toy paper")
    ap.add_argument("--paper", type=Path, default=DEFAULT_PAPER, help="toy paper directory")
    a = ap.parse_args(argv)
    paper = a.paper

    print("ScholarForge demo. Synthetic toy paper, offline, no model calls.")
    print(f"paper: {paper.name}  (all values in it are synthetic and invented)")

    section(1, "Provenance check: every number macro must resolve to a run-artifact value")
    prov = provenance_audit.audit(paper / "main.tex", paper / "macros_map.json")
    print(provenance_audit.render(prov))

    section(2, "Style scan: filler phrases in the body text")
    print(style_scan.render(style_scan.scan_path(paper / "main.tex"), lines=True))

    section(3, "Mock submit-gate: checks run in parallel through the orchestrator")
    rows, trace = submit_gate.run_gate([str(paper)])
    print("\n".join(trace.lines))
    print()
    print(submit_gate.render_matrix(rows))
    print(submit_gate.render_details(rows))

    section(4, "Control run: the same gate on a repaired copy of the toy paper")
    with tempfile.TemporaryDirectory() as t:
        fixed = Path(t) / "toy-paper-fixed"
        shutil.copytree(paper, fixed)
        repair(fixed)
        rows2, _ = submit_gate.run_gate([str(fixed)])
        print(submit_gate.render_matrix(rows2))

    planted_found = prov.hard_failures and rows[0]["verdict"] == "BLOCKED"
    control_clean = rows2[0]["verdict"] == "CLEAN"
    print("\nSummary")
    print(f"  planted problems detected on the toy paper: {'yes' if planted_found else 'NO'}")
    print(f"  repaired copy passes every gate:            {'yes' if control_clean else 'NO'}")
    return 0 if (planted_found and control_clean) else 1


if __name__ == "__main__":
    sys.exit(main())
