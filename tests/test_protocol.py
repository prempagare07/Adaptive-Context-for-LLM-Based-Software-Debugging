"""Regression coverage for malformed model actions and recovery in both modes."""
import json

import pytest

from adaptive_context.adaptive import AdaptiveDebugger
from adaptive_context.baseline import StaticRAG
from adaptive_context.chunking import chunk_source
from adaptive_context.llm import LLMReply
from adaptive_context.protocol import parse_reply, to_diagnosis
from adaptive_context.retrieval import BM25Retriever


def diagnosis(**changes):
    return {"action": "diagnose", "file": "payment.py", "function": "checkout",
            "cause": "The discounted return value is discarded.",
            "fix": "return apply_discount(price, discount)", "confidence": "high", **changes}


class ScriptedLLM:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.prompts = []

    def complete(self, system, user):
        self.prompts.append(user)
        return LLMReply(json.dumps(next(self.replies)), 1, 1, 0.0)


def retriever():
    return BM25Retriever(chunk_source("payment.py", "def checkout(price, discount):\n    return price\n"))


def test_empty_diagnosis_is_rejected_at_both_boundaries():
    assert parse_reply('{"action":"diagnose"}') is None
    assert not to_diagnosis({"action": "diagnose"}).valid


@pytest.mark.parametrize("field", ["file", "function", "cause", "fix", "confidence"])
def test_missing_diagnosis_field_is_rejected(field):
    obj = diagnosis()
    del obj[field]
    assert parse_reply(json.dumps(obj)) is None
    assert not to_diagnosis(obj).valid


@pytest.mark.parametrize("changes", [
    {"file": 7}, {"function": ["checkout"]}, {"cause": None},
    {"fix": None}, {"confidence": True}, {"confidence": "certain"},
    {"file": " "}, {"function": "Cart."}, {"cause": "\n"},
])
def test_invalid_diagnosis_values_are_not_coerced_to_strings(changes):
    obj = diagnosis(**changes)
    assert parse_reply(json.dumps(obj)) is None
    assert not to_diagnosis(obj).valid


@pytest.mark.parametrize("confidence", ["high", "low"])
def test_complete_diagnosis_allows_empty_fix_and_qualified_function(confidence):
    obj = diagnosis(function="Cart.checkout", fix="", confidence=confidence)
    parsed = parse_reply("model preamble\n" + json.dumps(obj) + "\nmodel postscript")
    result = to_diagnosis(parsed)
    assert result.valid and result.function == "checkout"
    assert result.fix == "" and result.confidence == confidence


@pytest.mark.parametrize("obj", [
    {"action": "request"}, {"action": "request", "symbols": [], "queries": []},
    {"action": "request", "symbols": "checkout"},
    {"action": "request", "symbols": [7]},
    {"action": "request", "symbols": [" "]},
    {"action": "request", "symbols": ["checkout"], "queries": None},
    {"action": "request", "queries": {"query": "discount"}},
])
def test_invalid_requests_are_rejected_before_the_loop_uses_them(obj):
    assert parse_reply(json.dumps(obj)) is None


@pytest.mark.parametrize("obj", [
    {"action": "request", "symbols": ["checkout"]},
    {"action": "request", "queries": ["discount return value"]},
])
def test_request_can_supply_either_nonempty_list(obj):
    assert parse_reply(json.dumps(obj)) == obj


def test_static_mode_does_not_report_empty_diagnosis_as_success():
    result = StaticRAG(retriever(), ScriptedLLM([{"action": "diagnose"}])).run("checkout discount")
    assert not result.diagnosis.valid
    assert result.stats.failures == 1


def test_adaptive_mode_recovers_after_invalid_diagnosis():
    llm = ScriptedLLM([{"action": "diagnose"}, diagnosis()])
    result = AdaptiveDebugger(retriever(), llm, max_rounds=2).run("checkout discount")
    assert result.diagnosis.valid and result.diagnosis.function == "checkout"
    assert result.stats.failures == 1 and result.stats.llm_calls == 2
    assert result.trace[0]["invalid"] is True
    assert "action schema" in llm.prompts[1]


def test_invalid_request_types_do_not_crash_adaptive_retrieval():
    llm = ScriptedLLM([{"action": "request", "symbols": 7}, diagnosis()])
    result = AdaptiveDebugger(retriever(), llm, max_rounds=2).run("checkout discount")
    assert result.diagnosis.valid and result.stats.failures == 1


def test_repeated_invalid_replies_exhaust_rounds_without_a_valid_diagnosis():
    llm = ScriptedLLM([{"action": "diagnose"}] * 2)
    result = AdaptiveDebugger(retriever(), llm, max_rounds=2).run("checkout discount")
    assert not result.diagnosis.valid
    assert result.stats.llm_calls == result.stats.failures == 2
