"""HUMAN REFERENCE FIX, written by hand for the delivery rehearsal only.

Not produced by any model. It exists to show that the five fixed tests can be
satisfied and are scored as expected. It is never a model result.
"""

import csv


class MissingColumnError(ValueError):
    """Raised when the CSV has no email column."""


def import_contacts(path):
    """Return [{"name": ..., "email": ...}, ...] for the rows in `path`, by column name."""
    records = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if "email" not in fields:
            raise MissingColumnError("CSV has no 'email' column")
        for row in reader:
            records.append({"name": row.get("name") or "", "email": row.get("email") or ""})
    return records
