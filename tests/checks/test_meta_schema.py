from pathlib import Path

from level.checks.meta_schema import MetaSchema
from level.config import Config, Context


def _context(tmp_path: Path) -> Context:
    return Context(
        home=tmp_path,
        config_file=tmp_path / "config.toml",
        config=Config(data_dir=tmp_path, editor=None, auto_open=False),
    )


def test_meta_schema_noop(tmp_path):
    context = _context(tmp_path)

    entity = tmp_path / "item"
    entity.mkdir()

    check = MetaSchema()

    findings = check.lint(context, entity)

    # Currently a no-op check
    assert findings == []
