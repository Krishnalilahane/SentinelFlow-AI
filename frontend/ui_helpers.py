def format_label(value: str | None) -> str:
    if not value:
        return "Not Available"

    return value.replace("_", " ").title()


def short_id(value: str | None, length: int = 8) -> str:
    if not value:
        return "N/A"

    return f"{value[:length]}..."


def case_display_name(case: dict) -> str:
    return (
        f"{short_id(case.get('id'))} | "
        f"{format_label(case.get('case_type'))} | "
        f"{format_label(case.get('state'))} | "
        f"{format_label(case.get('priority'))}"
    )


def format_number(value):
    if value is None:
        return "N/A"

    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}"

    return str(value)


def status_badge_text(value: str | None) -> str:
    return format_label(value)