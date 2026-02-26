def render_dict(data: dict[str, str]) -> str:
    """
    Render a dict as a simple key-value list for display.
    """
    lines = (f"{k}: {v}" for k, v in data.items())
    return "\n".join(lines)

def render_list(items: list[str]) -> str:
    """
    Render a list of strings as a bullet list for display.
    """
    lines = (f" * {item}" for item in items)
    return "\n".join(lines)


def render_table(rows: list[dict[str, str]], headers: list[str]) -> str:
    """
    Render a list of dicts as a simple table for display.
    """
    # Calculate column widths
    col_widths = {h: max(len(h), *(len(row.get(h, "")) for row in rows)) for h in headers}

    # Header row
    header_row = " | ".join(f"{h:{col_widths[h]}}" for h in headers)
    separator = "-+-".join("-" * col_widths[h] for h in headers)

    # Data rows
    data_rows = []
    for row in rows:
        data_row = " | ".join(f"{row.get(h, ''):{col_widths[h]}}" for h in headers)
        data_rows.append(data_row)

    return "\n".join([header_row, separator] + data_rows)
