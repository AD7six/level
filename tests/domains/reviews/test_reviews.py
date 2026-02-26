from dataclasses import replace
from datetime import date

import pytest

from level.config import build_context
from level.domains.reviews import reviews as review_module

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _context(tmp_path, monkeypatch):
    monkeypatch.setenv("LEVEL_HOME", str(tmp_path))
    context = build_context()
    new_config = replace(context.config, data_dir=tmp_path)
    return replace(context, config=new_config)


# ---------------------------------------------------------------------------
# functional tests (black-box behavior)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("period", ["weekly", "monthly", "quarterly", "annual"])
def test_review_lifecycle(tmp_path, monkeypatch, period):
    """
    Functional test:

    - Create review
    - Verify canonical directory created
    - Break canonical name
    - Lint detects issue
    - Fix repairs structure
    - Lint clean again
    """

    context = _context(tmp_path, monkeypatch)

    # Create review via public API
    review = review_module.Review(date=date(2026, 2, 20), period=period)
    review_module.save_review(context, review)

    review_id = review_module._review_id(review.date, review.period)
    canonical_dir = tmp_path / "reviews" / review_id

    # Canonical directory created
    assert canonical_dir.exists()
    assert (canonical_dir / "meta.toml").exists()

    # Lint clean initially
    assert review_module.lint_reviews(context) == []

    # Break canonical structure
    broken_dir = tmp_path / "reviews" / "wrong-name"
    canonical_dir.rename(broken_dir)

    # Lint detects issue
    issues = review_module.lint_reviews(context)
    assert issues

    # Fix structure
    actions = review_module.fix_reviews(context)
    assert any("Renamed" in action.message for action in actions)

    # Canonical restored
    assert canonical_dir.exists()
    assert review_module.lint_reviews(context) == []
