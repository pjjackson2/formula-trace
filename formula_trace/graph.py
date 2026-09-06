"""Build precedent/dependent maps from a sheet of formulas and walk them."""

from collections import deque

from .refs import extract_references


def read_formula_rows(source):
    """Yield (cell, formula) pairs from a 'cell,formula' CSV, tolerant of column order."""
    import csv

    reader = csv.DictReader(source)
    if reader.fieldnames is None:
        return

    fields_by_lower = {name.strip().lower(): name for name in reader.fieldnames}
    if "cell" not in fields_by_lower or "formula" not in fields_by_lower:
        raise ValueError("input must have 'cell' and 'formula' columns")

    cell_field = fields_by_lower["cell"]
    formula_field = fields_by_lower["formula"]

    for row in reader:
        cell = (row.get(cell_field) or "").strip()
        if not cell:
            continue
        yield cell.upper(), row.get(formula_field, "")


def build_precedents(rows):
    """Map each cell to the set of cells its own formula reads from."""
    precedents = {}
    for cell, formula in rows:
        precedents[cell] = extract_references(formula)
    return precedents


def build_dependents(precedents):
    """Invert a precedents map into cell -> set of cells that read from it."""
    dependents = {}
    for cell, refs in precedents.items():
        for ref in refs:
            dependents.setdefault(ref, set()).add(cell)
    return dependents


def transitive_closure(start, adjacency):
    """Breadth-first walk of adjacency from start, not including start itself."""
    seen = set()
    queue = deque(adjacency.get(start, ()))
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        queue.extend(adjacency.get(node, ()))
    return seen
