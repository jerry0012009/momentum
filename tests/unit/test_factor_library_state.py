"""Test factor library state generation."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def test_state_builds():
    """build_factor_library_state.py produces valid JSON + MD."""
    from build_factor_library_state import build_state
    state = build_state()
    assert isinstance(state, dict)
    assert "registered_factors" in state
    assert "computed_factor_values" in state
    assert "missing_factor_values" in state


def test_registered_count_not_hardcoded():
    """Registered count should be >= 60 (current repo has 65)."""
    from build_factor_library_state import build_state
    state = build_state()
    assert state["registered_factors"] >= 60, f"Expected >= 60, got {state['registered_factors']}"


def test_computed_plus_missing_equals_registered():
    """computed + missing should equal registered."""
    from build_factor_library_state import build_state
    state = build_state()
    total = state["computed_factor_values"] + state["missing_factor_values"]
    assert total == state["registered_factors"], (
        f"computed ({state['computed_factor_values']}) + missing ({state['missing_factor_values']}) "
        f"= {total} != registered ({state['registered_factors']})"
    )


def test_state_has_required_fields():
    """State dict should contain all required fields."""
    from build_factor_library_state import build_state
    state = build_state()
    required = [
        "generated_at", "dataset_id", "registered_factors", "computed_factor_values",
        "missing_factor_values", "missing_input_factors", "active_signal_factors",
        "signal_variants", "horizons", "factor_lifecycle_distribution",
        "candidate_review_distribution", "current_signal_factor_ids",
        "missing_input_factor_ids", "canonical_paths", "warnings", "disclaimer",
    ]
    for field in required:
        assert field in state, f"Missing required field: {field}"


def test_state_json_md_output(tmp_path):
    """build_factor_library_state writes JSON and MD files."""
    from build_factor_library_state import build_state, write_json, write_markdown
    state = build_state()
    json_path = write_json(state, tmp_path)
    md_path = write_markdown(state, tmp_path)
    assert json_path.exists()
    assert md_path.exists()
    # JSON round-trip
    with open(json_path) as f:
        loaded = json.load(f)
    assert loaded["registered_factors"] == state["registered_factors"]
    # MD has content
    content = md_path.read_text()
    assert "Factor Library State" in content


def test_signal_variants_not_zero():
    """signal_variants should be > 0 (currently 3 from canonical artifacts)."""
    from build_factor_library_state import build_state
    state = build_state()
    assert state["signal_variants"] > 0, (
        f"signal_variants is {state['signal_variants']}. "
        f"Should be derived from canonical signal artifacts (expected 3)."
    )


def test_signal_factor_ids_from_canonical_artifact():
    """current_signal_factor_ids should come from a canonical artifact, not code constant."""
    from build_factor_library_state import build_state
    state = build_state()
    source = state.get("signal_factor_source", "")
    assert "FALLBACK" not in source, (
        f"signal_factor_source is '{source}' — using code constant fallback. "
        f"Expected canonical artifact (phase9b_signal_component_manifest.csv or similar)."
    )
    assert state["active_signal_factors"] == 10, (
        f"Expected 10 signal factors, got {state['active_signal_factors']}"
    )


def test_no_fallback_warnings_for_signal():
    """No warnings about signal fallback if canonical artifacts exist."""
    from build_factor_library_state import build_state
    state = build_state()
    for w in state["warnings"]:
        assert "code constant" not in w.lower(), f"Unexpected fallback warning: {w}"
        assert "FALLBACK" not in w, f"Unexpected fallback warning: {w}"
