from collections.abc import Callable, Iterable


def render_dict(data: dict[str, str]) -> str:
    """
    Render a dict as a simple key-value list for display.
    """
    lines = (f"{k}: {v}" for k, v in data.items())
    return "\n".join(lines)


def render_list(items: Iterable[str], bullet: str = " * ") -> str:
    """
    Render a list of strings as a bullet list for display.
    """
    return render_objects(items, lambda x: x, bullet=bullet)


def render_objects[T](
    items: Iterable[T],
    formatter: Callable[[T], str],
    bullet: str = "",
) -> str:
    """
    Render a list of objects using a custom formatter and optional bullet.
    """
    return "\n".join(f"{bullet}{formatter(item)}" for item in items)


# Grouped rendering helper
def render_grouped_rows(
    rows: Iterable[dict[str, str]],
    *,
    group_key: str,
    row_formatter: Callable[[dict[str, str]], str],
    group_header_formatter: Callable[[str], str] | None = None,
) -> str:
    """
    Render rows grouped by a specific key.

    rows must already be sorted by group_key.
    """
    lines: list[str] = []
    current_group: str | None = None

    for row in rows:
        group_value = row.get(group_key, "")

        if group_value != current_group:
            if current_group is not None:
                lines.append("")

            header = (
                group_header_formatter(group_value)
                if group_header_formatter
                else group_value
            )
            lines.append(header)
            current_group = group_value

        lines.append(row_formatter(row))

    return "\n".join(lines)


def render_kv_block(data: dict[str, str]) -> str:
    """
    Render a dict as aligned key-value pairs for display.
    """
    width = max(len(k) for k in data.keys())
    lines = [f"{k:<{width}}  {v}" for k, v in data.items()]
    return "\n".join(lines)


def render_table(rows: list[dict[str, str]], columns: dict[str, str]) -> str:
    """
    Render a list of dicts as a simple table for display.
    """
    if not rows:
        return ""

    keys = list(columns.keys())
    headers = list(columns.values())

    col_widths = {
        header: max(len(header), *(len(str(row.get(key, ""))) for row in rows))
        for key, header in zip(keys, headers, strict=True)
    }

    data_widths = col_widths.copy()
    if headers:
        data_widths[headers[-1]] += 1

    header_row = " | ".join(headers)

    if len(headers) == 1:
        separator = "-" * data_widths[headers[0]]
    else:
        segments = ["-" * (data_widths[headers[0]] + 1)] + [
            "-" * (data_widths[header] + 2) for header in headers[1:]
        ]
        separator = "+".join(segments)

    data_rows = []
    for row in rows:
        data_row = " | ".join(
            f"{str(row.get(key, '')):{data_widths[header]}}"
            for key, header in zip(keys, headers, strict=True)
        )
        data_rows.append(data_row)

    return "\n".join([header_row, separator] + data_rows)
