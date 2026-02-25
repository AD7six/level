from pathlib import Path

from level.config import Config, Context
from level.core.doctor import CanonicalDomain, fix_domain, lint_domain


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def test_lint_domain_detects_non_canonical(tmp_path):
    context = _context(tmp_path)

    root = tmp_path / "domain"
    root.mkdir()

    wrong = root / "wrong"
    wrong.mkdir()

    def finder(ctx):
        return [wrong]

    def canonical_rel(ctx, entity):
        return root / "expected"

    domain = CanonicalDomain(
        finder=finder,
        canonical_rel=canonical_rel,
        root_resolver=lambda ctx: root,
    )

    issues = lint_domain(context, domain)

    assert issues == ["Non-canonical directory: wrong (expected expected)"]


def test_fix_domain_renames_to_canonical(tmp_path):
    context = _context(tmp_path)

    root = tmp_path / "domain"
    root.mkdir()

    wrong = root / "wrong"
    wrong.mkdir()

    def finder(ctx):
        return [wrong]

    def canonical_rel(ctx, entity):
        return root / "expected"

    domain = CanonicalDomain(
        finder=finder,
        canonical_rel=canonical_rel,
        root_resolver=lambda ctx: root,
    )

    actions = fix_domain(context, domain)

    assert actions == ["Renamed wrong -> expected"]
    assert (root / "expected").exists()


def test_lint_domain_ignores_canonical(tmp_path):
    context = _context(tmp_path)

    root = tmp_path / "domain"
    root.mkdir()

    correct = root / "expected"
    correct.mkdir()

    def finder(ctx):
        return [correct]

    def canonical_rel(ctx, entity):
        return root / "expected"

    domain = CanonicalDomain(
        finder=finder,
        canonical_rel=canonical_rel,
        root_resolver=lambda ctx: root,
    )

    issues = lint_domain(context, domain)

    assert issues == []
