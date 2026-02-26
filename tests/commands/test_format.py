from level.commands._format import (
    render_dict,
    render_list,
    render_table,
    render_kv_block,
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

    expected = (
        "Short           A\n"
        "Much Longer Key B"
    )

    assert output == expected


def test_render_table():
    rows = [
        {"name": "Alice", "role": "Engineer"},
        {"name": "Bob", "role": "Manager"},
    ]
    headers = {"name": "Employee", "role": "Current Role"}

    output = render_table(rows, headers)

    expected = (
        "Employee | Current Role \n"
        "---------+--------------\n"
        "Alice    | Engineer     \n"
        "Bob      | Manager      "
    )

    assert output == expected
