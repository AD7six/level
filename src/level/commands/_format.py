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

def render_kv_block(data: dict[str, str]) -> str:
    """
    Render a dict as aligned key-value pairs for display.
    """
    width = max(len(k) for k in data.keys())
    lines = [
        f"{k:<{width}}  {v}"
        for k, v in data.items()
    ]
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
        header: max(
            len(header),
            *(len(str(row.get(key, ""))) for row in rows)
        )
        for key, header in zip(keys, headers)
    }

    header_row = " | ".join(
        f"{header:{col_widths[header]}}"
        for header in headers
    )
    separator = "-+-".join("-" * col_widths[header] for header in headers)

    data_rows = []
    for row in rows:
        data_row = " | ".join(
            f"{str(row.get(key, '')):{col_widths[header]}}"
            for key, header in zip(keys, headers)
        )
        data_rows.append(data_row)

    return "\n".join([header_row, separator] + data_rows)
