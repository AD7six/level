from pathlib import Path

from level.config import Config, Context
from level.core.doctor import Domain, lint_domain, fix_domain
from level.checks.base import Check, Finding
from level.core.doctor import FixResult


class DummyCheck(Check):
    name = "dummy"

    def lint(self, context: Context, entity: Path) -> list[Finding]:
        if entity.name == "wrong":
            return [Finding("wrong name", fixable=True)]
        return []

    def fix(self, context: Context, entity: Path) -> list[FixResult]:
        new_path = entity.parent / "expected"
        entity.rename(new_path)
        return [
            FixResult(
                entity=new_path,
                check_name=self.name,
                message="Renamed wrong -> expected",
            )
        ]


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def test_lint_domain_detects_issue(tmp_path):
    context = _context(tmp_path)

    root = tmp_path / "domain"
    root.mkdir()

    wrong = root / "wrong"
    wrong.mkdir()

    domain = Domain(
        finder=lambda ctx: [wrong],
        checks=[DummyCheck()],
    )

    findings = lint_domain(context, domain)

    assert len(findings) == 1
    assert findings[0].message == "wrong name"


def test_fix_domain_applies_fix(tmp_path):
    context = _context(tmp_path)

    root = tmp_path / "domain"
    root.mkdir()

    wrong = root / "wrong"
    wrong.mkdir()

    domain = Domain(
        finder=lambda ctx: [wrong],
        checks=[DummyCheck()],
    )

    results = fix_domain(context, domain)

    assert len(results) == 1
    assert results[0].message == "Renamed wrong -> expected"
    assert (root / "expected").exists()


def test_lint_domain_no_issue(tmp_path):
    context = _context(tmp_path)

    root = tmp_path / "domain"
    root.mkdir()

    correct = root / "expected"
    correct.mkdir()

    domain = Domain(
        finder=lambda ctx: [correct],
        checks=[DummyCheck()],
    )

    findings = lint_domain(context, domain)

    assert findings == []
