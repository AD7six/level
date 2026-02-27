import pytest

from level.commands._format import (
    render_dict,
    render_grouped_rows,
    render_kv_block,
    render_list,
    render_objects,
    render_table,
)


def test_render_dict():
    data = {"Name": "Alice", "Role": "Engineer"}
    output = render_dict(data)

    # Order is insertion order in Python 3.7+
    assert output == "Name: Alice\nRole: Engineer"


def test_render_list():
    items = ["one", "two"]
    output = render_list(items)

    assert output == " * one\n * two"


def test_render_kv_block():
    data = {
        "Short": "A",
        "Much Longer Key": "B",
    }

    output = render_kv_block(data)

    expected = "Short            A\n" "Much Longer Key  B"

    assert output == expected


def test_render_table():
    rows = [
        {"name": "Alice", "role": "Engineer"},
        {"name": "Bob", "role": "Manager"},
    ]
    headers = {"name": "Employee", "role": "Current Role"}

    output = render_table(rows, headers)

    expected = (
        "Employee | Current Role\n"
        "---------+---------------\n"
        "Alice    | Engineer     \n"
        "Bob      | Manager      "
    )

    assert output == expected


def test_render_list_custom_bullet():
    assert render_list(["a"], bullet="- ") == "- a"


def test_render_list_empty():
    assert render_list([]) == ""


def test_render_objects_custom_formatter():
    output = render_objects([1, 2], lambda x: f"[{x}]")
    assert output == "[1]\n[2]"


def test_render_grouped_rows_basic():
    rows = [
        {"state": "Open", "slug": "a"},
        {"state": "Open", "slug": "b"},
        {"state": "Closed", "slug": "c"},
    ]

    output = render_grouped_rows(
        rows,
        group_key="state",
        row_formatter=lambda r: r["slug"],
    )

    expected = "Open\na\nb\n\nClosed\nc"
    assert output == expected


def test_render_grouped_rows_single_group():
    rows = [
        {"state": "Open", "slug": "a"},
        {"state": "Open", "slug": "b"},
    ]

    output = render_grouped_rows(
        rows,
        group_key="state",
        row_formatter=lambda r: r["slug"],
    )

    assert output == "Open\na\nb"


def test_render_grouped_rows_empty():
    assert (
        render_grouped_rows(
            [],
            group_key="state",
            row_formatter=lambda r: r["slug"],
        )
        == ""
    )


def test_render_kv_block_empty():
    with pytest.raises(ValueError):
        render_kv_block({})


def test_render_table_empty():
    assert render_table([], {"a": "A"}) == ""


def test_render_table_single_row():
    rows = [{"a": "1"}]
    headers = {"a": "Col"}

    output = render_table(rows, headers)
    assert "Col" in output
    assert "1" in output


def test_render_table_missing_key():
    rows = [{"a": "1"}, {"b": "2"}]
    headers = {"a": "ColA", "b": "ColB"}

    output = render_table(rows, headers)
    assert "ColA" in output
    assert "ColB" in output
    assert "1" in output
    assert "2" in output
