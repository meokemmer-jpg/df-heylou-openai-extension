from __future__ import annotations

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from function_definitions import (
    HEYLOU_FUNCTION_DEFINITIONS,
    build_tool_payload,
    get_function_names,
)


def _openai_function_names(payload: dict) -> list[str]:
    return [tool["function"]["name"] for tool in payload["tools"]]


def test_openai_extension_payload_discriminates_against_gemini_countercase():
    openai_payload = build_tool_payload(provider="openai")
    counter_payload = build_tool_payload(provider=" GEMINI ")

    assert "tools" in openai_payload
    assert "function_declarations" not in openai_payload
    assert all(tool["type"] == "function" for tool in openai_payload["tools"])

    assert "function_declarations" in counter_payload
    assert "tools" not in counter_payload

    assert openai_payload != counter_payload
    assert json.dumps(openai_payload, sort_keys=True) != json.dumps(counter_payload, sort_keys=True)
    assert _openai_function_names(openai_payload) == get_function_names()
    assert [fd["name"] for fd in counter_payload["function_declarations"]] == get_function_names()


def test_openai_payload_is_derived_from_real_schema_not_test_constants():
    payload = build_tool_payload(provider="openai")

    assert len(payload["tools"]) == len(HEYLOU_FUNCTION_DEFINITIONS)
    for tool, definition in zip(payload["tools"], HEYLOU_FUNCTION_DEFINITIONS):
        assert tool["function"]["name"] == definition["name"]
        assert tool["function"]["description"] == definition["description"]
        assert tool["function"]["parameters"] == definition["parameters"]

    payload["tools"][0]["function"]["parameters"]["required"].append("test_mutation")
    assert "test_mutation" not in HEYLOU_FUNCTION_DEFINITIONS[0]["parameters"]["required"]


def test_unknown_provider_is_rejected_instead_of_falling_back_to_static_output():
    with pytest.raises(ValueError, match="unsupported tool provider"):
        build_tool_payload(provider="anthropic")
