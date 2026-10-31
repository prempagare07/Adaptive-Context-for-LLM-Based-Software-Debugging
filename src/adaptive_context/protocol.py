"""Prompts and reply parsing shared by every debugger."""
from __future__ import annotations

import json
import re

from .compress import LEVELS
from .models import Diagnosis

SYSTEM_BASE = """You are a senior engineer debugging a Python repository. You receive a bug report and code excerpts.
Find the root cause: the single function that contains the defect. Reply with ONE JSON object and nothing else.
Diagnose format:
{"action":"diagnose","file":"<path>","function":"<name>","cause":"<one sentence citing evidence from the excerpts>","fix":"<corrected single line of code, or empty>","confidence":"high|low"}
Only cite code that appears in the excerpts. If evidence is missing, set confidence to low."""

SYSTEM_ADAPTIVE = SYSTEM_BASE + """
If the excerpts lack the evidence and ALLOWED_ACTIONS includes request, ask for more context instead of guessing:
{"action":"request","symbols":["<function names to fetch>"],"queries":["<short search text>"]}
Excerpts may be trimmed (see the bracket tag on each header). Request a symbol to see its full body.
Prefer symbols over queries when you know the name."""


def render_context(items: list) -> str:
    return "\n".join(
        f"### {p.chunk.path}::{p.chunk.name} (L{p.chunk.start}-{p.chunk.end}) [{LEVELS[p.level]}]\n```python\n{p.text}\n```"
        for p in items)


def build_user_prompt(bug_report: str, context: str, allowed: str, round_no: int, max_rounds: int, note: str = "") -> str:
    return (f"BUG REPORT:\n{bug_report}\n\nROUND: {round_no}/{max_rounds}\nALLOWED_ACTIONS: {allowed}\n"
            f"{note}\nCONTEXT:\n{context}\n")


def _valid_diagnosis(obj) -> bool:
    """Validate the response shape, independently of diagnosis correctness."""
    if not isinstance(obj, dict) or obj.get("action") != "diagnose":
        return False
    if not all(isinstance(obj.get(key), str) and obj[key].strip()
               for key in ("file", "function", "cause")):
        return False
    return (bool(obj["function"].rsplit(".", 1)[-1].strip())
            and isinstance(obj.get("fix"), str)
            and obj.get("confidence") in ("high", "low"))


def _valid_request(obj) -> bool:
    if not isinstance(obj, dict) or obj.get("action") != "request":
        return False
    symbols, queries = obj.get("symbols", []), obj.get("queries", [])
    return (isinstance(symbols, list) and isinstance(queries, list)
            and bool(symbols or queries)
            and all(isinstance(value, str) and value.strip() for value in symbols + queries))


def parse_reply(text: str):
    """Find a supported action with correctly typed, complete fields."""
    if not isinstance(text, str):
        return None
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", text):
        try:
            obj, _ = dec.raw_decode(text[m.start():])
        except ValueError:
            continue
        if _valid_diagnosis(obj) or _valid_request(obj):
            return obj
    return None


def to_diagnosis(obj: dict) -> Diagnosis:
    if not _valid_diagnosis(obj):
        return Diagnosis()
    return Diagnosis(file=obj["file"].strip(), function=obj["function"].rsplit(".", 1)[-1].strip(),
                     cause=obj["cause"].strip(), fix=obj["fix"],
                     confidence=obj["confidence"], valid=True)
