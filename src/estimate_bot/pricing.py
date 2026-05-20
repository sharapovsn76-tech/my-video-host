"""Default price catalog and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from estimate_bot.models import ItemCategory, as_decimal


@dataclass(frozen=True)
class Rate:
    name: str
    unit: str
    unit_price: Decimal
    category: ItemCategory
    aliases: tuple[str, ...] = ()


DEFAULT_RATES: tuple[Rate, ...] = (
    Rate(
        name="tile installation labor",
        unit="m2",
        unit_price=Decimal("1800"),
        category=ItemCategory.LABOR,
        aliases=("укладка плитки", "работа плитка", "tile labor", "tile installation"),
    ),
    Rate(
        name="ceramic tile",
        unit="m2",
        unit_price=Decimal("1200"),
        category=ItemCategory.MATERIAL,
        aliases=("плитка", "керамическая плитка", "tile", "ceramic tile"),
    ),
    Rate(
        name="wall painting labor",
        unit="m2",
        unit_price=Decimal("450"),
        category=ItemCategory.LABOR,
        aliases=("покраска", "painting labor", "paint labor"),
    ),
    Rate(
        name="interior paint",
        unit="l",
        unit_price=Decimal("650"),
        category=ItemCategory.MATERIAL,
        aliases=("краска", "paint", "interior paint"),
    ),
    Rate(
        name="drywall sheet",
        unit="sheet",
        unit_price=Decimal("520"),
        category=ItemCategory.MATERIAL,
        aliases=("гкл", "гипсокартон", "drywall", "drywall sheet"),
    ),
    Rate(
        name="drywall installation labor",
        unit="m2",
        unit_price=Decimal("900"),
        category=ItemCategory.LABOR,
        aliases=("монтаж гкл", "монтаж гипсокартона", "drywall labor"),
    ),
)


def normalize_text(value: str) -> str:
    return " ".join(value.casefold().replace("ё", "е").split())


class PriceCatalog:
    """Simple in-memory price catalog suitable for MVP bot flows."""

    def __init__(self, rates: tuple[Rate, ...] = DEFAULT_RATES) -> None:
        self._rates = rates

    def find(self, description: str) -> Rate | None:
        normalized = normalize_text(description)
        best_match: Rate | None = None
        best_alias_length = 0

        for rate in self._rates:
            names = (rate.name, *rate.aliases)
            for alias in names:
                normalized_alias = normalize_text(alias)
                if normalized_alias and normalized_alias in normalized:
                    if len(normalized_alias) > best_alias_length:
                        best_match = rate
                        best_alias_length = len(normalized_alias)

        return best_match

    def require(self, description: str) -> Rate:
        rate = self.find(description)
        if rate is None:
            raise KeyError(f"No default rate found for: {description}")
        return rate

    def with_rate(
        self,
        name: str,
        unit: str,
        unit_price: Decimal | int | float | str,
        category: ItemCategory,
        aliases: tuple[str, ...] = (),
    ) -> "PriceCatalog":
        return PriceCatalog(
            self._rates
            + (
                Rate(
                    name=name,
                    unit=unit,
                    unit_price=as_decimal(unit_price),
                    category=category,
                    aliases=aliases,
                ),
            )
        )
