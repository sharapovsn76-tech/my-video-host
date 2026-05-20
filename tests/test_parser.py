from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from estimate_bot.models import ItemCategory
from estimate_bot.parser import parse_estimate_request


class EstimateParserTests(unittest.TestCase):
    def test_parses_russian_request_with_explicit_prices_and_markup(self) -> None:
        estimate = parse_estimate_request(
            "плитка 25 м2 по 1200 руб/м2, работа 25 м2 по 1800 руб/м2, наценка 15%"
        )

        self.assertEqual(len(estimate.line_items), 2)
        self.assertEqual(estimate.markup_percent, Decimal("15"))
        self.assertEqual(estimate.direct_total, Decimal("75000.00"))
        self.assertEqual(estimate.markup_amount, Decimal("11250.00"))
        self.assertEqual(estimate.grand_total, Decimal("86250.00"))
        self.assertEqual(estimate.line_items[0].category, ItemCategory.MATERIAL)
        self.assertEqual(estimate.line_items[1].category, ItemCategory.LABOR)

    def test_uses_catalog_price_when_price_is_omitted(self) -> None:
        estimate = parse_estimate_request("плитка 10 м2")

        self.assertEqual(estimate.line_items[0].unit_price, Decimal("1200.00"))
        self.assertEqual(estimate.grand_total, Decimal("12000.00"))

    def test_parses_tax_percent(self) -> None:
        estimate = parse_estimate_request("краска 5 л по 650, ндс 20%")

        self.assertEqual(estimate.tax_percent, Decimal("20"))
        self.assertEqual(estimate.tax_amount, Decimal("650.00"))
        self.assertEqual(estimate.grand_total, Decimal("3900.00"))

    def test_requires_price_for_unknown_catalog_item(self) -> None:
        with self.assertRaises(ValueError):
            parse_estimate_request("нестандартная позиция 3 м2")


if __name__ == "__main__":
    unittest.main()
