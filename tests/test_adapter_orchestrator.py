"""Tests for OpenAIAdapterOrchestrator [CRUX-MK]."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from src.adapter_orchestrator import OpenAIAdapterOrchestrator, LoopReport


def setup_function(_):
    for k in (
        "DF_HEYLOU_OPENAI_EXT_ENABLED",
        "DF_HEYLOU_OPENAI_TENANT_ID",
        "OPENAI_API_KEY",
        "PHRONESIS_TICKET",
    ):
        os.environ.pop(k, None)


def test_orchestrator_defaults_to_sandbox():
    orch = OpenAIAdapterOrchestrator()
    assert orch.sandbox_mode is True
    assert orch.PROVIDER == "gemini"
    assert orch.DF_ID == "df-heylou-openai-extension"


def test_run_sandbox_completes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    orch = OpenAIAdapterOrchestrator()
    report = orch.run()
    assert isinstance(report, LoopReport)
    assert report.sandbox_mode is True
    # In sandbox: alle 4 Phasen sollten passieren
    assert "auth" in report.phases_passed
    assert "health" in report.phases_passed
    assert "sample" in report.phases_passed
    assert "audit_persist" in report.phases_passed
    assert report.final_status in ("complete", "partial")


def test_loop_report_persisted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    orch = OpenAIAdapterOrchestrator()
    report = orch.run()
    expected = tmp_path / "runs" / "loop-reports" / f"loop-{report.loop_id}.json"
    assert expected.exists()


def test_function_count_artifact():
    orch = OpenAIAdapterOrchestrator()
    report = orch.run(dry_run=True)
    assert report.artifacts.get("function_count") == 5
    assert isinstance(report.artifacts.get("functions"), list)
