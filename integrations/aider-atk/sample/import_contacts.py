"""Read a contacts CSV into a list of records.

This is the file the task asks you to change. The tests next to it are fixed:
they describe the behaviour that is wanted, and two of them fail today.
"""

import csv


class MissingColumnError(ValueError):
    """Raised when the CSV has no email column."""


def import_contacts(path):
    """Return [{"name": ..., "email": ...}, ...] for the rows in `path`.

    Today this reads by position: the first column is the name and the second
    is the email. A file that puts email first is read backwards, and a file
    with no email column raises whatever Python happens to raise.
    """
    records = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader, None)  # header
        for row in reader:
            if not row:
                continue
            records.append({"name": row[0], "email": row[1]})
    return records
