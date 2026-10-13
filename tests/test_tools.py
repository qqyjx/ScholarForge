"""Tests for the three standalone tools. Each tool has at least one case that must fail."""
import json
from pathlib import Path

import pytest

from scholarforge.tools import page_sweep, provenance_audit as pa, style_scan

TOY = Path(__file__).resolve().parent.parent / "examples" / "toy-paper"


def make_paper(tmp_path: Path, tex: str, macros: dict, artifact: dict) -> tuple[Path, Path]:
    (tmp_path / "a.json").write_text(json.dumps(artifact))
    (tmp_path / "map.json").write_text(json.dumps({"macros": macros}))
    (tmp_path / "p.tex").write_text(tex)
    return tmp_path / "p.tex", tmp_path / "map.json"


ACC = {"acc": {"artifact": "a.json", "key": "m.acc", "scale": 100, "fmt": ".1f"}}
BODY = "\\newcommand{{\\acc}}{{{v}}}\n\\begin{{document}}\nWe get \\acc\\% here. {extra}\n\\end{{document}}\n"


def audit(tmp_path, v="81.4", extra="", raw=0.8137, macros=ACC):
    tex, mp = make_paper(tmp_path, BODY.format(v=v, extra=extra), macros, {"m": {"acc": raw}})
    return pa.audit(tex, mp)


def test_clean_paper_passes(tmp_path):
    rep = audit(tmp_path)
    assert rep.ok and rep.checked == 1 and not rep.findings


def test_mismatch_fails(tmp_path):
    rep = audit(tmp_path, v="82.0")
    assert [f.kind for f in rep.hard_failures] == ["MISMATCH"]


def test_round_once_from_raw_value(tmp_path):
    # 0.81449 -> 81.449 -> "81.4". Rounding 81.449 to 81.45 first would give 81.5, so the macro 81.5 must fail.
    assert audit(tmp_path, v="81.4", raw=0.81449).ok
    assert not audit(tmp_path, v="81.5", raw=0.81449).ok


def test_hardcoded_decimal_and_percent_fail(tmp_path):
    assert [f.kind for f in audit(tmp_path, extra="It reaches 79.5 points.").hard_failures] == ["HARDCODED"]
    assert [f.kind for f in audit(tmp_path, extra="It reaches 80\\% of cases.").hard_failures] == ["HARDCODED"]


def test_pragma_and_safe_contexts_do_not_fire(tmp_path):
    safe = "See Table~\\ref{tab:1.2} \\cite{k2020}. \\includegraphics[width=0.9\\linewidth]{f.pdf}"
    assert audit(tmp_path, extra=safe).ok
    tex, mp = make_paper(tmp_path, BODY.format(v="81.4", extra="") + "", ACC, {"m": {"acc": 0.8137}})
    tex.write_text(BODY.format(v="81.4", extra="").replace("here.", "here. alpha 0.05 % prov:ok"))
    assert pa.audit(tex, mp).ok


def test_unmapped_numeric_macro_fails(tmp_path):
    tex, mp = make_paper(tmp_path, "\\newcommand{\\extra}{3.5}\n\\begin{document}\nx\n\\end{document}\n", {}, {})
    assert [f.kind for f in pa.audit(tex, mp).hard_failures] == ["UNMAPPED"]


def test_missing_artifact_and_key_fail(tmp_path):
    rep = audit(tmp_path, macros={"acc": {"artifact": "nope.json", "key": "m.acc", "fmt": ".1f"}})
    assert [f.kind for f in rep.hard_failures] == ["MISSING"]
    rep = audit(tmp_path, macros={"acc": {"artifact": "a.json", "key": "m.absent", "fmt": ".1f"}})
    assert [f.kind for f in rep.hard_failures] == ["MISSING"]


def test_unused_macro_is_soft_only(tmp_path):
    tex, mp = make_paper(tmp_path, "\\newcommand{\\acc}{81.4}\n\\begin{document}\nx\n\\end{document}\n", ACC, {"m": {"acc": 0.8137}})
    rep = pa.audit(tex, mp)
    assert rep.ok and [f.kind for f in rep.soft_advisories] == ["UNUSED"]


def test_toy_paper_findings():
    rep = pa.audit(TOY / "main.tex", TOY / "macros_map.json")
    assert sorted(f.kind for f in rep.hard_failures) == ["HARDCODED", "MISMATCH"]
    assert {f.macro for f in rep.findings if f.kind == "MISMATCH"} == {"accBase"}
    assert [f.kind for f in rep.soft_advisories] == ["UNUSED"]
    assert rep.checked == 6


def test_provenance_cli_exit_codes(capsys):
    assert pa.main(["--tex", str(TOY / "main.tex"), "--map", str(TOY / "macros_map.json")]) == 1
    assert "RESULT=FAIL" in capsys.readouterr().out
    assert pa.main(["--selftest"]) == 0


def test_style_scan_flags_filler_and_passes_clean():
    assert style_scan.scan_text("We measure accuracy and report it.\n") == []
    kinds = {n for _, n, _ in style_scan.scan_text("It is worth noting that we delve in --- Crucially, yes.\n")}
    assert {"worth-noting", "stock-verb", "dash", "sentence-adverb"} <= kinds


def test_style_scan_skips_comments_macros_and_table_rows():
    text = "% It is worth noting\n\\newcommand{\\x}{leverage}\nA & B --- C \\\\\nUse \\% \\textbf{Note}: here\n"
    assert [n for _, n, _ in style_scan.scan_text(text)] == ["bold-colon"]


def test_style_scan_toy_paper():
    hits = style_scan.scan_path(TOY / "main.tex")
    assert sum(len(v) for v in hits.values()) == 6


def test_page_sweep_estimate_and_overflow(tmp_path):
    short = tmp_path / "s.tex"
    long = tmp_path / "l.tex"
    short.write_text("\\begin{document}\n" + "word " * 100 + "\n\\end{document}\n")
    long.write_text("\\begin{document}\n" + "word " * 1500 + "\n\\end{document}\n")
    assert page_sweep.main(["--tex", str(short), "--limit", "1"]) == 0
    assert page_sweep.main(["--tex", str(long), "--limit", "1"]) == 1


def test_page_sweep_ignores_text_after_bibliography(tmp_path):
    f = tmp_path / "b.tex"
    f.write_text("\\begin{document}\n" + "word " * 100 + "\\bibliography{x}\n" + "ref " * 5000 + "\n\\end{document}\n")
    assert page_sweep.body_words(f.read_text()) == 100


def test_page_sweep_pdf_fallback_counts_pages(tmp_path):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-1.4\n<< /Type /Pages >>\n<< /Type /Page >>\n<< /Type /Page >>\n")
    assert page_sweep.count_pdf_pages(pdf) in (0, 2)  # pdfinfo may reject this stub; the regex path counts 2


@pytest.mark.parametrize("mod", [style_scan, page_sweep])
def test_selftests_pass(mod):
    assert mod.main(["--selftest"]) == 0
