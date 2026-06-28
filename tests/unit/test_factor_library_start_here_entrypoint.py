"""Guards for README -> START_HERE factor-library entrypoint."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
START_HERE = ROOT / "docs" / "factor_library" / "START_HERE.md"


def test_readme_points_factor_library_work_to_start_here():
    text = README.read_text()
    text_lower = text.lower()

    assert "The only developer entry point for factor-library work is" in text
    assert "docs/factor_library/START_HERE.md" in text
    for boundary in ["production", "live trading", "investment advice", "alpha verification"]:
        assert boundary in text_lower


def test_start_here_contains_public_factor_and_taxonomy_entrypoints():
    text = START_HERE.read_text()

    required = [
        "docs/factor_library/public_factor_candidate_manifest.csv",
        "docs/factor_library/INDUSTRY_NEUTRALIZATION_DATA_CONTRACT.md",
        "data/sources/crypto_industry_taxonomy_contract_v1/symbol_taxonomy.template.csv",
        "scripts/init_crypto_industry_taxonomy_review.py",
        "scripts/build_crypto_industry_taxonomy_artifact.py",
        "scripts/check_crypto_industry_taxonomy_contract.py",
        "scripts/check_crypto_industry_taxonomy_coverage.py",
        "scripts/factor_formula_registry.py",
        "scripts/run_factor_intake.py",
        "scripts/run_post_intake_workflow_completion.py",
        "scripts/check_post_intake_workflow_integrity.py",
        "scripts/check_factor_evaluation_page_completeness.py",
        "scripts/build_factor_library_state.py",
    ]
    for needle in required:
        assert needle in text


def test_start_here_keeps_factor_intake_boundaries_visible():
    text = START_HERE.read_text()

    assert "Do not add intake factors directly to `scripts/build_phase9b_signal_panel.py`" in text
    assert "Do not modify live trading, broker, exchange, or execution code" in text
    assert "Do not hand-write factor counts" in text
