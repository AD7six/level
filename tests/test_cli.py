def test_build_parser():
    from level.cli import build_parser
    parser = build_parser(prog_name="level")
    assert parser is not None
