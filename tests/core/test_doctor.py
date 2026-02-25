from pathlib import Path

from level.config import Config, Context
from level.core.doctor import DomainDoctor, fix_domain, lint_domain


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def test_lint_domain_runs_all_linters(tmp_path):
    context = _context(tmp_path)

    entities = [tmp_path / "a", tmp_path / "b"]
    for e in entities:
        e.mkdir()

    def finder(ctx):
        return entities

    def l1(ctx, entity):
        return [f"l1:{entity.name}"]

    def l2(ctx, entity):
        return [f"l2:{entity.name}"]

    doctor = DomainDoctor(finder=finder, linters=[l1, l2], fixers=[])

    issues = lint_domain(context, doctor)

    assert issues == [
        "l1:a",
        "l2:a",
        "l1:b",
        "l2:b",
    ]


def test_fix_domain_runs_all_fixers(tmp_path):
    context = _context(tmp_path)

    entities = [tmp_path / "x"]
    entities[0].mkdir()

    def finder(ctx):
        return entities

    def f1(ctx, entity):
        return [f"f1:{entity.name}"]

    def f2(ctx, entity):
        return [f"f2:{entity.name}"]

    doctor = DomainDoctor(finder=finder, linters=[], fixers=[f1, f2])

    actions = fix_domain(context, doctor)

    assert actions == ["f1:x", "f2:x"]


def test_lint_domain_handles_linter_exception(tmp_path):
    context = _context(tmp_path)

    entity = tmp_path / "e"
    entity.mkdir()

    def finder(ctx):
        return [entity]

    def bad_linter(ctx, entity):
        raise RuntimeError("boom")

    doctor = DomainDoctor(finder=finder, linters=[bad_linter], fixers=[])

    issues = lint_domain(context, doctor)

    assert len(issues) == 1
    assert "Linter error" in issues[0]


def test_fix_domain_handles_fixer_exception(tmp_path):
    context = _context(tmp_path)

    entity = tmp_path / "e"
    entity.mkdir()

    def finder(ctx):
        return [entity]

    def bad_fixer(ctx, entity):
        raise RuntimeError("boom")

    doctor = DomainDoctor(finder=finder, linters=[], fixers=[bad_fixer])

    actions = fix_domain(context, doctor)

    assert len(actions) == 1
    assert "Fixer error" in actions[0]
