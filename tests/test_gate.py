"""Tests for the orchestrator, the mock submit-gate and the demo."""
import shutil
import time
from pathlib import Path

import pytest

from scholarforge import demo, orchestrator as orch, submit_gate

TOY = Path(__file__).resolve().parent.parent / "examples" / "toy-paper"


def good(gate="g", hard=(), soft=()):
    verdict = "FAIL" if hard else ("WARN" if soft else "PASS")
    return {"gate": gate, "verdict": verdict, "hard_failures": list(hard), "soft_advisories": list(soft), "evidence": []}


def test_validate_gate_accepts_good_and_rejects_bad():
    assert orch.validate_gate(good())["verdict"] == "PASS"
    with pytest.raises(orch.SchemaError):
        orch.validate_gate({"gate": "g"})                      # missing fields
    with pytest.raises(orch.SchemaError):
        orch.validate_gate({**good(), "verdict": "MAYBE"})     # not in the enum
    with pytest.raises(orch.SchemaError):
        orch.validate_gate({**good(hard=["x"]), "verdict": "PASS"})  # verdict contradicts the lists


def test_plimit_keeps_order_and_caps_concurrency():
    running, peak = [0], [0]
    import threading
    lock = threading.Lock()

    def work(i):
        def f():
            with lock:
                running[0] += 1
                peak[0] = max(peak[0], running[0])
            time.sleep(0.02)
            with lock:
                running[0] -= 1
            return i
        return orch.Agent(f"a{i}", f)

    out = orch.plimit([work(i) for i in range(8)], n=3)
    assert out == list(range(8))
    assert peak[0] <= 3


def test_guard_must_fail_on_mismatch():
    orch.guard("/a/b\n", "/a/b")
    with pytest.raises(orch.RepoGuardError):
        orch.guard("/other", "/a/b")


def test_compliance_levels():
    rows = [{"item": "a", "verdict": None, "gates": [good(), good(soft=["s"])]},
            {"item": "b", "verdict": None, "gates": [good(hard=["h"]), good(soft=["s"])]},
            {"item": "c", "verdict": None, "gates": [good(), good()]},
            {"item": "d", "verdict": "SKIPPED", "gates": []}]
    assert [r["verdict"] for r in orch.compliance(rows)] == ["WARN", "BLOCKED", "CLEAN", "SKIPPED"]


def test_toy_paper_is_blocked_with_expected_gates():
    rows, trace = submit_gate.run_gate([str(TOY)])
    by = {g["gate"]: g["verdict"] for g in rows[0]["gates"]}
    assert by == {"provenance": "FAIL", "style": "WARN", "layout": "PASS", "anon": "PASS"}
    assert rows[0]["verdict"] == "BLOCKED"
    assert any("provenance:toy-paper" in l for l in trace.lines)


def test_anon_gate_fails_on_forbidden_string(tmp_path):
    paper = tmp_path / "p"
    shutil.copytree(TOY, paper)
    with (paper / "main.tex").open("a") as f:
        f.write("% Jane Doe\n")
    rows, _ = submit_gate.run_gate([str(paper)])
    anon = next(g for g in rows[0]["gates"] if g["gate"] == "anon")
    assert anon["verdict"] == "FAIL"


def test_layout_gate_fails_when_limit_is_tiny():
    rows, _ = submit_gate.run_gate([str(TOY)], page_limit=0.01)
    assert next(g for g in rows[0]["gates"] if g["gate"] == "layout")["verdict"] == "FAIL"


def test_missing_main_tex_is_skipped(tmp_path):
    rows, _ = submit_gate.run_gate([str(tmp_path)])
    assert rows[0]["verdict"] == "SKIPPED"


def test_repaired_copy_is_clean(tmp_path):
    fixed = tmp_path / "fixed"
    shutil.copytree(TOY, fixed)
    demo.repair(fixed)
    rows, _ = submit_gate.run_gate([str(fixed)])
    assert rows[0]["verdict"] == "CLEAN"


def test_matrix_rendering_has_one_row_per_paper():
    rows, _ = submit_gate.run_gate([str(TOY)])
    lines = submit_gate.render_matrix(rows).splitlines()
    assert len(lines) == 3 and lines[2].split()[-1] == "BLOCKED"


def test_demo_runs_and_reports_success(capsys):
    assert demo.main([]) == 0
    out = capsys.readouterr().out
    assert "planted problems detected on the toy paper: yes" in out
    assert "repaired copy passes every gate:            yes" in out


def test_demo_output_is_deterministic(capsys):
    demo.main([]); a = capsys.readouterr().out
    demo.main([]); b = capsys.readouterr().out
    assert a == b
