from tkcalendar import DateEntry
from datetime import datetime
from app.ui.theme import FONT_FAMILY


def make_date_picker(parent, **kwargs) -> DateEntry:
    """Styled DateEntry -- calendar popup, ISO-format string output.
    .get() returns 'YYYY-MM-DD' directly, matching what the DB/services expect.
    No free-text entry possible, so malformed dates can't happen."""
    return DateEntry(
        parent,
        date_pattern="yyyy-mm-dd",
        font=(FONT_FAMILY, 12),
        background="#3B5BDB",
        foreground="white",
        bordercolor="#D8DEE9",
        headersbackground="#3B5BDB",
        headersforeground="white",
        selectbackground="#3B5BDB",
        normalbackground="white",
        weekendbackground="#F5F7FC",
        **kwargs
    )


def set_date_value(date_entry: DateEntry, iso_string: str):
    """Used when loading a batch row back into the form for editing."""
    if not iso_string:
        return
    try:
        date_entry.set_date(datetime.strptime(iso_string, "%Y-%m-%d").date())
    except ValueError:
        pass  # leave picker on its default (today) if the stored value is malformed