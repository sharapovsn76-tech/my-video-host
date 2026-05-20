from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from estimate_bot.materials import (
    calculate_drywall_sheets,
    calculate_paint_liters,
    calculate_tile_area,
)


class MaterialCalculationTests(unittest.TestCase):
    def test_calculates_tile_area_with_waste(self) -> None:
        quantity = calculate_tile_area("25", waste_percent="10")

        self.assertEqual(quantity.name, "ceramic tile")
        self.assertEqual(quantity.quantity, Decimal("27.50"))
        self.assertEqual(quantity.unit, "m2")

    def test_calculates_paint_liters_for_two_coats(self) -> None:
        quantity = calculate_paint_liters("100", coats=2, coverage_m2_per_liter="10", waste_percent="10")

        self.assertEqual(quantity.quantity, Decimal("22.00"))
        self.assertEqual(quantity.unit, "l")

    def test_rounds_drywall_sheets_up(self) -> None:
        quantity = calculate_drywall_sheets("25", sheet_area_m2="3", waste_percent="10")

        self.assertEqual(quantity.quantity, Decimal("10"))
        self.assertEqual(quantity.unit, "sheet")


if __name__ == "__main__":
    unittest.main()
