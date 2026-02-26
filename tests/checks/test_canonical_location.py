from pathlib import Path

from level.checks.canonical_location import CanonicalLocation
from level.config import Config, Context


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def _root(context: Context) -> Path:
    data_dir = context.config.data_dir
    assert data_dir is not None

    root = data_dir / "items"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _canonical_rel(context: Context, entity: Path) -> Path | None:
    # Canonical path is always <root>/expected
    return _root(context) / "expected"


def test_lint_detects_non_canonical(tmp_path):
    context = _context(tmp_path)
    root = _root(context)

    wrong = root / "wrong"
    wrong.mkdir()

    check = CanonicalLocation(_canonical_rel, _root)

    findings = check.lint(context, wrong)

    assert len(findings) == 1
    assert "Non-canonical directory" in findings[0].message
    assert findings[0].fixable is True


def test_lint_allows_valid_suffix(tmp_path):
    context = _context(tmp_path)
    root = _root(context)

    suffixed = root / "expected-1"
    suffixed.mkdir()

    check = CanonicalLocation(_canonical_rel, _root)

    findings = check.lint(context, suffixed)

    assert findings == []


def test_fix_renames_to_canonical(tmp_path):
    context = _context(tmp_path)
    root = _root(context)

    wrong = root / "wrong"
    wrong.mkdir()

    check = CanonicalLocation(_canonical_rel, _root)

    results = check.fix(context, wrong)

    assert len(results) == 1
    assert (root / "expected").exists()
    assert not wrong.exists()


def test_fix_resolves_collision(tmp_path):
    context = _context(tmp_path)
    root = _root(context)

    # Existing canonical
    (root / "expected").mkdir()

    wrong = root / "wrong"
    wrong.mkdir()

    check = CanonicalLocation(_canonical_rel, _root)

    results = check.fix(context, wrong)

    assert len(results) == 1
    assert (root / "expected-1").exists()
    assert not wrong.exists()
