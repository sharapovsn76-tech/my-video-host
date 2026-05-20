"""Material quantity helpers for common renovation tasks."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING

from estimate_bot.models import as_decimal


@dataclass(frozen=True)
class MaterialQuantity:
    name: str
    quantity: Decimal
    unit: str
    assumptions: tuple[str, ...] = ()


def _with_waste(quantity: Decimal, waste_percent: Decimal) -> Decimal:
    return quantity * (Decimal("1") + waste_percent / Decimal("100"))


def calculate_tile_area(
    area_m2: Decimal | int | float | str,
    waste_percent: Decimal | int | float | str = Decimal("10"),
) -> MaterialQuantity:
    area = as_decimal(area_m2)
    waste = as_decimal(waste_percent)
    total = _with_waste(area, waste)
    return MaterialQuantity(
        name="ceramic tile",
        quantity=total.quantize(Decimal("0.01")),
        unit="m2",
        assumptions=(f"{waste}% waste included",),
    )


def calculate_paint_liters(
    area_m2: Decimal | int | float | str,
    coats: int = 2,
    coverage_m2_per_liter: Decimal | int | float | str = Decimal("10"),
    waste_percent: Decimal | int | float | str = Decimal("10"),
) -> MaterialQuantity:
    if coats <= 0:
        raise ValueError("coats must be positive")

    area = as_decimal(area_m2)
    coverage = as_decimal(coverage_m2_per_liter)
    waste = as_decimal(waste_percent)
    if coverage <= 0:
        raise ValueError("coverage_m2_per_liter must be positive")

    liters = _with_waste(area * coats / coverage, waste)
    return MaterialQuantity(
        name="interior paint",
        quantity=liters.quantize(Decimal("0.01")),
        unit="l",
        assumptions=(f"{coats} coats", f"{coverage} m2/l coverage", f"{waste}% waste included"),
    )


def calculate_drywall_sheets(
    area_m2: Decimal | int | float | str,
    sheet_area_m2: Decimal | int | float | str = Decimal("3"),
    waste_percent: Decimal | int | float | str = Decimal("10"),
) -> MaterialQuantity:
    area = as_decimal(area_m2)
    sheet_area = as_decimal(sheet_area_m2)
    waste = as_decimal(waste_percent)
    if sheet_area <= 0:
        raise ValueError("sheet_area_m2 must be positive")

    sheets = (_with_waste(area, waste) / sheet_area).to_integral_value(rounding=ROUND_CEILING)
    return MaterialQuantity(
        name="drywall sheet",
        quantity=sheets,
        unit="sheet",
        assumptions=(f"{sheet_area} m2 per sheet", f"{waste}% waste included"),
    )
