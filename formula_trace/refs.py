"""Extract cell references out of a spreadsheet formula string."""

import re
import string

_SHEET_PREFIX = r"(?:'[^']+'|[A-Za-z_][A-Za-z0-9_]*)!"
_CELL = r"\$?[A-Za-z]{1,3}\$?[0-9]+"

RANGE_RE = re.compile(
    r"(?P<sheet>" + _SHEET_PREFIX + r")?(?P<start>" + _CELL + r"):(?P<end>" + _CELL + r")"
)
CELL_RE = re.compile(r"(?P<sheet>" + _SHEET_PREFIX + r")?(?P<cell>" + _CELL + r")")

_SPLIT_RE = re.compile(r"\$?([A-Za-z]{1,3})\$?([0-9]+)")


def _column_to_index(letters):
    letters = letters.upper()
    index = 0
    for ch in letters:
        index = index * 26 + (string.ascii_uppercase.index(ch) + 1)
    return index


def _index_to_column(index):
    letters = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = string.ascii_uppercase[remainder] + letters
    return letters


def _normalize_sheet(sheet):
    if not sheet:
        return ""
    sheet = sheet[:-1]  # drop trailing '!'
    if sheet.startswith("'") and sheet.endswith("'"):
        sheet = sheet[1:-1]
    return sheet + "!"


def _expand_range(sheet, start, end):
    start_match = _SPLIT_RE.fullmatch(start)
    end_match = _SPLIT_RE.fullmatch(end)
    if not start_match or not end_match:
        return {sheet + start.upper(), sheet + end.upper()}

    start_col, start_row = _column_to_index(start_match.group(1)), int(start_match.group(2))
    end_col, end_row = _column_to_index(end_match.group(1)), int(end_match.group(2))
    if start_col > end_col:
        start_col, end_col = end_col, start_col
    if start_row > end_row:
        start_row, end_row = end_row, start_row

    cells = set()
    for col in range(start_col, end_col + 1):
        for row in range(start_row, end_row + 1):
            cells.add(sheet + _index_to_column(col) + str(row))
    return cells


def extract_references(formula):
    """Return the set of cell references (e.g. {"A1", "Sheet2!B3"}) a formula reads from."""
    if formula is None:
        return set()

    references = set()
    remaining = formula

    for match in RANGE_RE.finditer(formula):
        sheet = _normalize_sheet(match.group("sheet"))
        references.update(_expand_range(sheet, match.group("start"), match.group("end")))
        remaining = remaining.replace(match.group(0), " ", 1)

    for match in CELL_RE.finditer(remaining):
        sheet = _normalize_sheet(match.group("sheet"))
        references.add(sheet + match.group("cell").replace("$", "").upper())

    return references
