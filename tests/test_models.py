from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from estimate_bot.models import Estimate, ItemCategory, LineItem


class EstimateModelTests(unittest.TestCase):
    def test_line_item_applies_waste_to_subtotal(self) -> None:
        item = LineItem(
            description="ceramic tile",
            quantity="10",
            unit="m2",
            unit_price="1200",
            category=ItemCategory.MATERIAL,
            waste_percent="10",
        )

        self.assertEqual(item.billable_quantity, Decimal("11.0"))
        self.assertEqual(item.subtotal, Decimal("13200.00"))

    def test_estimate_totals_markup_and_tax(self) -> None:
        estimate = Estimate(project_name="Bathroom", markup_percent="15", tax_percent="20")
        estimate.add_item(LineItem("tile", "10", "m2", "1000", ItemCategory.MATERIAL))
        estimate.add_item(LineItem("labor", "10", "m2", "2000", ItemCategory.LABOR))

        self.assertEqual(estimate.direct_total, Decimal("30000.00"))
        self.assertEqual(estimate.markup_amount, Decimal("4500.00"))
        self.assertEqual(estimate.tax_amount, Decimal("6900.00"))
        self.assertEqual(estimate.grand_total, Decimal("41400.00"))

    def test_rejects_invalid_quantity(self) -> None:
        with self.assertRaises(ValueError):
            LineItem("bad item", "0", "m2", "100")


if __name__ == "__main__":
    unittest.main()
