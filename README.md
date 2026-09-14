# formula-trace

Once a spreadsheet has been passed around for a while, nobody knows what
touches what. You want to change one cell and need to know what else will
move, or you're staring at a formula and want to know everything it actually
reads from. `formula-trace` answers that one question from the command line,
given a plain export of the sheet's cells and formulas.

It does not open `.xlsx` files itself (see the roadmap below). Feed it a CSV
with `cell` and `formula` columns instead - most spreadsheet tools can export
that directly, or you can build it with a short script.

## Usage

Given `sheet.csv`:

```csv
cell,formula
A1,10
A2,20
B1,=A1+A2
B2,=SUM(A1:A2)
C1,=B1*B2
```

Ask what `C1` depends on, transitively:

```
$ formula-trace sheet.csv --cell C1
A1
A2
B1
B2
```

Ask what would be affected if `A1` changes:

```
$ formula-trace sheet.csv --cell A1 --direction dependents
B1
B2
C1
```

Only want the direct references, not the whole chain:

```
$ formula-trace sheet.csv --cell C1 --direct-only
B1
B2
```

It also reads from stdin, so it fits into a pipeline without a temp file:

```
$ cat sheet.csv | formula-trace --cell C1
A1
A2
B1
B2
```

Pass `--format json` to get a single JSON object instead of one cell per line,
for feeding the result into another tool:

```
$ formula-trace sheet.csv --cell C1 --format json
{"cell": "C1", "direction": "precedents", "direct_only": false, "references": ["A1", "A2", "B1", "B2"]}
```

## Install

No dependencies beyond the standard library.

```
$ pip install -e .
```

or just run it in place:

```
$ python -m formula_trace.cli sheet.csv --cell C1
```

## Formula syntax it understands

- Plain references: `A1`, `$B$2`
- Ranges: `A1:A10`, expanded into every cell in the rectangle
- Sheet-qualified references: `Sheet2!A1`, `'My Sheet'!A1:B4`

It does not evaluate formulas, only reads the cell references out of them.

## Known limitations

- A function name that happens to look like a cell reference (`LOG10`,
  for example) will currently be picked up as one. Rare in practice, but
  worth knowing about.
- Ranges spanning two sheets (`Sheet1!A1:Sheet2!B2`) aren't handled.
- No circular reference detection yet - a cycle in the formulas will just
  make the transitive closure include everything in the cycle, silently.
