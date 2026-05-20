"""Core domain objects for construction estimates."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import StrEnum


MONEY_QUANT = Decimal("0.01")


class ItemCategory(StrEnum):
    """High-level category for an estimate line item."""

    MATERIAL = "material"
    LABOR = "labor"
    EQUIPMENT = "equipment"
    OTHER = "other"


def as_decimal(value: Decimal | int | float | str) -> Decimal:
    """Convert numeric input to Decimal without inheriting float artifacts."""

    if isinstance(value, Decimal):
        return value
    return Decimal(str(value).replace(",", "."))


def money(value: Decimal | int | float | str) -> Decimal:
    """Round a Decimal-compatible value to cents."""

    return as_decimal(value).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class LineItem:
    """A single material, labor, equipment, or miscellaneous estimate row."""

    description: str
    quantity: Decimal | int | float | str
    unit: str
    unit_price: Decimal | int | float | str
    category: ItemCategory = ItemCategory.OTHER
    waste_percent: Decimal | int | float | str = Decimal("0")
    note: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "quantity", as_decimal(self.quantity))
        object.__setattr__(self, "unit_price", money(self.unit_price))
        object.__setattr__(self, "waste_percent", as_decimal(self.waste_percent))

        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.unit_price < 0:
            raise ValueError("unit_price cannot be negative")
        if self.waste_percent < 0:
            raise ValueError("waste_percent cannot be negative")

    @property
    def billable_quantity(self) -> Decimal:
        multiplier = Decimal("1") + (self.waste_percent / Decimal("100"))
        return self.quantity * multiplier

    @property
    def subtotal(self) -> Decimal:
        return money(self.billable_quantity * self.unit_price)


@dataclass
class Estimate:
    """An itemized estimate with markup and optional tax."""

    project_name: str
    line_items: list[LineItem] = field(default_factory=list)
    markup_percent: Decimal | int | float | str = Decimal("0")
    tax_percent: Decimal | int | float | str = Decimal("0")
    assumptions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.markup_percent = as_decimal(self.markup_percent)
        self.tax_percent = as_decimal(self.tax_percent)

        if self.markup_percent < 0:
            raise ValueError("markup_percent cannot be negative")
        if self.tax_percent < 0:
            raise ValueError("tax_percent cannot be negative")

    def add_item(self, item: LineItem) -> None:
        self.line_items.append(item)

    @property
    def direct_total(self) -> Decimal:
        return money(sum((item.subtotal for item in self.line_items), Decimal("0")))

    @property
    def markup_amount(self) -> Decimal:
        return money(self.direct_total * self.markup_percent / Decimal("100"))

    @property
    def taxable_total(self) -> Decimal:
        return money(self.direct_total + self.markup_amount)

    @property
    def tax_amount(self) -> Decimal:
        return money(self.taxable_total * self.tax_percent / Decimal("100"))

    @property
    def grand_total(self) -> Decimal:
        return money(self.taxable_total + self.tax_amount)

    def to_dict(self) -> dict[str, object]:
        return {
            "project_name": self.project_name,
            "items": [
                {
                    "description": item.description,
                    "quantity": str(item.quantity),
                    "unit": item.unit,
                    "unit_price": str(item.unit_price),
                    "category": item.category.value,
                    "waste_percent": str(item.waste_percent),
                    "subtotal": str(item.subtotal),
                    "note": item.note,
                }
                for item in self.line_items
            ],
            "direct_total": str(self.direct_total),
            "markup_percent": str(self.markup_percent),
            "markup_amount": str(self.markup_amount),
            "tax_percent": str(self.tax_percent),
            "tax_amount": str(self.tax_amount),
            "grand_total": str(self.grand_total),
            "assumptions": list(self.assumptions),
        }
