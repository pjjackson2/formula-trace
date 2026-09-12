import unittest

from formula_trace.refs import (
    _column_to_index,
    _index_to_column,
    extract_references,
)


class ColumnIndexTests(unittest.TestCase):
    def test_single_letter_round_trips(self):
        for letters in ["A", "B", "Z"]:
            self.assertEqual(_index_to_column(_column_to_index(letters)), letters)

    def test_known_values(self):
        self.assertEqual(_column_to_index("A"), 1)
        self.assertEqual(_column_to_index("Z"), 26)
        self.assertEqual(_column_to_index("AA"), 27)
        self.assertEqual(_column_to_index("AZ"), 52)

    def test_lowercase_is_accepted(self):
        self.assertEqual(_column_to_index("a"), _column_to_index("A"))

    def test_double_letter_round_trips(self):
        for index in [27, 52, 100, 702]:
            self.assertEqual(_column_to_index(_index_to_column(index)), index)


class PlainReferenceTests(unittest.TestCase):
    def test_single_cell(self):
        self.assertEqual(extract_references("=A1"), {"A1"})

    def test_multiple_cells(self):
        self.assertEqual(extract_references("=A1+B2"), {"A1", "B2"})

    def test_absolute_dollar_signs_are_stripped(self):
        self.assertEqual(extract_references("=$A$1"), {"A1"})
        self.assertEqual(extract_references("=A$1+$A2"), {"A1", "A2"})

    def test_lowercase_column_is_uppercased(self):
        self.assertEqual(extract_references("=a1"), {"A1"})

    def test_none_formula_returns_empty_set(self):
        self.assertEqual(extract_references(None), set())

    def test_no_references_returns_empty_set(self):
        self.assertEqual(extract_references("=10"), set())


class RangeParsingTests(unittest.TestCase):
    def test_small_range_expands_every_cell(self):
        self.assertEqual(extract_references("=A1:A3"), {"A1", "A2", "A3"})

    def test_rectangular_range_expands_both_dimensions(self):
        self.assertEqual(
            extract_references("=A1:B2"),
            {"A1", "A2", "B1", "B2"},
        )

    def test_reversed_range_is_normalized(self):
        # end before start, either by column or row
        self.assertEqual(extract_references("=B2:A1"), {"A1", "A2", "B1", "B2"})

    def test_range_with_dollar_signs(self):
        self.assertEqual(extract_references("=$A$1:$A$3"), {"A1", "A2", "A3"})

    def test_range_inside_a_function_call(self):
        self.assertEqual(extract_references("=SUM(A1:A2)"), {"A1", "A2"})

    def test_range_does_not_also_yield_its_endpoints_as_plain_cells(self):
        # the naive CELL_RE pass over the leftover text shouldn't re-add A1/A3
        refs = extract_references("=SUM(A1:A3)+B1")
        self.assertEqual(refs, {"A1", "A2", "A3", "B1"})

    def test_multiple_ranges_in_one_formula(self):
        self.assertEqual(
            extract_references("=SUM(A1:A2,B1:B2)"),
            {"A1", "A2", "B1", "B2"},
        )


class SheetQualifiedTests(unittest.TestCase):
    def test_unquoted_sheet_name(self):
        self.assertEqual(extract_references("=Sheet2!A1"), {"Sheet2!A1"})

    def test_quoted_sheet_name_with_space(self):
        self.assertEqual(extract_references("='My Sheet'!A1"), {"My Sheet!A1"})

    def test_quoted_sheet_name_range(self):
        self.assertEqual(
            extract_references("='My Sheet'!A1:A2"),
            {"My Sheet!A1", "My Sheet!A2"},
        )

    def test_sheet_prefix_applies_to_whole_range_not_just_start(self):
        refs = extract_references("=Sheet2!A1:B2")
        self.assertEqual(refs, {"Sheet2!A1", "Sheet2!A2", "Sheet2!B1", "Sheet2!B2"})

    def test_mixed_local_and_sheet_qualified_refs(self):
        self.assertEqual(
            extract_references("=A1+Sheet2!A1"),
            {"A1", "Sheet2!A1"},
        )

    def test_different_sheets_are_distinct_references(self):
        refs = extract_references("=Sheet1!A1+Sheet2!A1")
        self.assertEqual(refs, {"Sheet1!A1", "Sheet2!A1"})


if __name__ == "__main__":
    unittest.main()
