from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from level.config import Context
from level.editor import open_in_editor

# ---------------------------------------------------------------------------
# model
# ---------------------------------------------------------------------------


@dataclass
class Review:
    date: date
    period: str  # "weekly" | "monthly" | "quarterly" | "annual"
    wins: list[str] = field(default_factory=list)
    challenges: list[str] = field(default_factory=list)
    learnings: list[str] = field(default_factory=list)
    next_focus: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date.isoformat(),
            "period": self.period,
            "wins": self.wins,
            "challenges": self.challenges,
            "learnings": self.learnings,
            "next_focus": self.next_focus,
        }

    @staticmethod
    def from_dict(data: dict[str, object]) -> Review:
        def _list_of_str(value: object) -> list[str]:
            if isinstance(value, list) and all(isinstance(x, str) for x in value):
                return value
            return []

        raw_date = data.get("date")
        raw_period = data.get("period")

        if not isinstance(raw_date, str):
            raise ValueError("Invalid or missing 'date' in review meta")

        if not isinstance(raw_period, str):
            raise ValueError("Invalid or missing 'period' in review meta")

        return Review(
            date=date.fromisoformat(raw_date),
            period=raw_period,
            wins=_list_of_str(data.get("wins")),
            challenges=_list_of_str(data.get("challenges")),
            learnings=_list_of_str(data.get("learnings")),
            next_focus=_list_of_str(data.get("next_focus")),
        )


# ---------------------------------------------------------------------------
# paths
# ---------------------------------------------------------------------------


def _reviews_dir(context: Context) -> Path:
    assert context.config.data_dir is not None
    return context.config.data_dir / "reviews"


# Canonical review period ID
def _review_id(review_date: date, period: str) -> str:
    if period == "weekly":
        iso_year, iso_week, _ = review_date.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"

    if period == "monthly":
        return f"{review_date.year}-{review_date.month:02d}"

    if period == "quarterly":
        quarter = (review_date.month - 1) // 3 + 1
        return f"{review_date.year}-Q{quarter}"

    if period == "annual":
        return f"{review_date.year}"

    raise ValueError(f"Unsupported review period: {period}")


def _review_dir(context: Context, review_date: date, period: str) -> Path:
    return _reviews_dir(context) / _review_id(review_date, period)


def _meta_path(context: Context, review_date: date, period: str) -> Path:
    return _review_dir(context, review_date, period) / "meta.toml"


# ---------------------------------------------------------------------------
# persistence
# ---------------------------------------------------------------------------


def save_review(context: Context, review: Review) -> None:
    review_path = _review_dir(context, review.date, review.period)
    review_path.mkdir(parents=True, exist_ok=True)

    meta_path = _meta_path(context, review.date, review.period)

    with meta_path.open("w", encoding="utf-8") as f:
        for key, value in review.to_dict().items():
            if isinstance(value, list):
                f.write(f"{key} = {value}\n")
            else:
                f.write(f'{key} = "{value}"\n')

    # Ensure notes.md exists
    notes_path = review_path / "notes.md"
    if not notes_path.exists():
        notes_path.write_text("# Review Notes\n\n", encoding="utf-8")

    # Open in editor (if enabled)
    open_in_editor(
        notes_path, auto_open=context.config.auto_open, editor=context.config.editor
    )


def load_review(context: Context, review_date: date, period: str) -> Review:
    meta_path = _meta_path(context, review_date, period)

    if not meta_path.exists():
        raise ValueError(f"Review not found for {review_date.isoformat()} ({period})")

    with meta_path.open("rb") as f:
        data = tomllib.load(f)

    return Review.from_dict(data)


def list_reviews(context: Context) -> list[Review]:
    root = _reviews_dir(context)

    if not root.exists():
        return []

    reviews: list[Review] = []

    for entry in sorted(root.iterdir()):
        if not entry.is_dir():
            continue

        meta_path = entry / "meta.toml"
        if not meta_path.exists():
            continue

        with meta_path.open("rb") as f:
            data = tomllib.load(f)

        reviews.append(Review.from_dict(data))

    return sorted(reviews, key=lambda r: r.date, reverse=True)


# ---------------------------------------------------------------------------
# lint / fix
# ---------------------------------------------------------------------------


def lint_reviews(context: Context) -> list[str]:
    issues: list[str] = []
    root = _reviews_dir(context)

    if not root.exists():
        issues.append("Reviews directory does not exist")
        return issues

    for entry in root.iterdir():
        if not entry.is_dir():
            continue

        meta_path = entry / "meta.toml"
        if not meta_path.exists():
            issues.append(f"Missing meta.toml in {entry.name}")
            continue

        try:
            with meta_path.open("rb") as f:
                data = tomllib.load(f)
            Review.from_dict(data)
        except Exception:
            issues.append(f"Invalid meta.toml in {entry.name}")

    return issues


def fix_reviews(context: Context) -> list[str]:
    actions: list[str] = []
    root = _reviews_dir(context)

    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
        actions.append("Created reviews directory")

    return actions
