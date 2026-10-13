"""A small orchestrator that mirrors the structure of the example workflows.

The workflows in `workflows/*.js` use four ideas. This module has the same four, in plain Python:

  agent       a named unit of work with a model tier and a phase label
  plimit      run a list of agents with at most `n` running at once
  pipeline    per item: a precheck stage, then a gate stage that fans out
  schema      every gate result is validated before it is used

In the demo the agents are local functions, not model calls. The tier is only a label here.
`LLMClient` is the interface a model-backed agent would use. The demo does not need one.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

TIERS = {"mechanical": "sonnet", "inspection": "opus", "bulk": "haiku"}
VERDICTS = ("PASS", "WARN", "FAIL")
GATE_FIELDS = ("gate", "verdict", "hard_failures", "soft_advisories", "evidence")


class LLMClient(Protocol):
    """Interface for a model-backed agent. Not used by the offline demo."""

    def complete(self, prompt: str) -> str: ...


class SchemaError(ValueError):
    """A gate returned a result that does not match the gate schema."""


class RepoGuardError(RuntimeError):
    """The path an agent reported does not match the path the caller expected."""


def validate_gate(result: dict[str, Any]) -> dict[str, Any]:
    """Check that a gate result has the required fields, a valid verdict, and a consistent verdict."""
    missing = [k for k in GATE_FIELDS if k not in result]
    if missing:
        raise SchemaError(f"gate result lacks fields: {missing}")
    if result["verdict"] not in VERDICTS:
        raise SchemaError(f"verdict must be one of {VERDICTS}, got {result['verdict']!r}")
    expected = "FAIL" if result["hard_failures"] else ("WARN" if result["soft_advisories"] else "PASS")
    if result["verdict"] != expected:
        raise SchemaError(f"verdict {result['verdict']} does not match the lists (expected {expected})")
    return result


@dataclass
class Agent:
    """One unit of work. `fn` takes no arguments and returns a result."""

    label: str
    fn: Callable[[], Any]
    tier: str = "mechanical"
    phase: str = ""
    schema: Callable[[dict], dict] | None = None

    def run(self) -> Any:
        out = self.fn()
        return self.schema(out) if self.schema else out


@dataclass
class Trace:
    """Ordered record of what ran. Output order does not depend on thread timing."""

    lines: list[str] = field(default_factory=list)

    def phase(self, title: str, detail: str = "") -> None:
        self.lines.append(f"== {title}" + (f": {detail}" if detail else ""))

    def agent(self, a: Agent, summary: str) -> None:
        self.lines.append(f"   {a.label:<22} tier={a.tier:<10} model~{TIERS.get(a.tier, '?'):<7} {summary}")


def plimit(agents: list[Agent], n: int = 3) -> list[Any]:
    """Run agents with at most `n` at once. Results keep the input order."""
    with ThreadPoolExecutor(max_workers=n) as pool:
        return list(pool.map(lambda a: a.run(), agents))


def guard(reported: str, expected: str) -> None:
    """Compare the path an agent reports with the path the caller expects."""
    if reported.strip() != expected:
        raise RepoGuardError(f"guard failed: agent saw {reported!r}, caller expected {expected!r}")


def pipeline(
    items: list[str],
    pre: Callable[[str], dict],
    gates: Callable[[dict, str], list[Agent]],
    trace: Trace,
    limit: int = 3,
) -> list[dict]:
    """For each item: run the precheck; if it passes, run the gate agents at most `limit` at a time."""
    rows = []
    for item in items:
        precheck = pre(item)
        guard(precheck["toplevel"], item)
        if not precheck["ok"]:
            rows.append({"item": item, "verdict": "SKIPPED", "gates": [], "precheck": precheck})
            continue
        agents = gates(precheck, item)
        results = plimit(agents, limit)
        for a, r in zip(agents, results):
            trace.agent(a, f"{r['verdict']}  hard={len(r['hard_failures'])} soft={len(r['soft_advisories'])}")
        rows.append({"item": item, "verdict": None, "gates": results, "precheck": precheck})
    return rows


def compliance(rows: list[dict]) -> list[dict]:
    """One verdict per item: BLOCKED if any gate failed, WARN if any warned, CLEAN otherwise."""
    out = []
    for r in rows:
        if r["verdict"] == "SKIPPED":
            out.append(r)
            continue
        v = ("BLOCKED" if any(g["verdict"] == "FAIL" for g in r["gates"])
             else "WARN" if any(g["verdict"] == "WARN" for g in r["gates"]) else "CLEAN")
        out.append({**r, "verdict": v})
    return out
