import argparse
import sys

from .graph import build_dependents, build_precedents, read_formula_rows, transitive_closure


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="formula-trace",
        description="Trace which cells a formula depends on, or which cells depend on it.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="CSV file with 'cell,formula' columns (default: read from stdin)",
    )
    parser.add_argument("--cell", required=True, help="cell to trace, e.g. B7 or Sheet2!B7")
    parser.add_argument(
        "--direction",
        choices=["precedents", "dependents"],
        default="precedents",
        help="precedents = cells this one reads from; dependents = cells that read from this one",
    )
    parser.add_argument(
        "--direct-only",
        action="store_true",
        help="show only direct references instead of the full transitive closure",
    )

    args = parser.parse_args(argv)
    target = args.cell.strip().upper()

    if args.file == "-":
        rows = list(read_formula_rows(sys.stdin))
    else:
        with open(args.file, newline="") as handle:
            rows = list(read_formula_rows(handle))

    precedents = build_precedents(rows)
    adjacency = precedents if args.direction == "precedents" else build_dependents(precedents)

    if args.direct_only:
        result = adjacency.get(target, set())
    else:
        result = transitive_closure(target, adjacency)

    for cell in sorted(result):
        print(cell)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
