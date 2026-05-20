"""Rule-based parser for short estimate requests."""

from __future__ import annotations

import re
from decimal import Decimal

from estimate_bot.models import Estimate, ItemCategory, LineItem, as_decimal
from estimate_bot.pricing import PriceCatalog


NUMBER = r"\d+(?:[.,]\d+)?"
UNIT = r"м2|м²|кв\.?\s*м|m2|sqm|шт|штук|sheet|sheets|л|литр(?:а|ов)?|l|пог\.?\s*м|lm"

LINE_RE = re.compile(
    rf"""
    (?P<description>.*?)
    (?P<quantity>{NUMBER})
    \s*
    (?P<unit>{UNIT})
    (?:
        \s*(?:по|x|х|@|at)\s*
        (?P<unit_price>{NUMBER})
        (?:\s*(?:руб\.?|р\.?|rub|₽))?
        (?:\s*/\s*(?:{UNIT}))?
    )?
    """,
    re.IGNORECASE | re.VERBOSE,
)

MARKUP_RE = re.compile(r"(?:наценка|маржа|markup)\s*(?P<value>\d+(?:[.,]\d+)?)\s*%", re.IGNORECASE)
TAX_RE = re.compile(r"(?:ндс|tax|vat)\s*(?P<value>\d+(?:[.,]\d+)?)\s*%", re.IGNORECASE)

LABOR_HINTS = ("работ", "монтаж", "уклад", "покраск", "установк", "labor", "install")
MATERIAL_HINTS = ("материал", "плитк", "краск", "гкл", "гипсокартон", "material", "tile", "paint", "drywall")


def normalize_unit(unit: str) -> str:
    normalized = " ".join(unit.casefold().replace("ё", "е").split())
    if normalized in {"м2", "м²", "кв. м", "кв м", "m2", "sqm"}:
        return "m2"
    if normalized in {"шт", "штук", "sheet", "sheets"}:
        return "pcs"
    if normalized in {"л", "литр", "литра", "литров", "l"}:
        return "l"
    if normalized in {"пог. м", "пог м", "lm"}:
        return "lm"
    return normalized


def _extract_percent(pattern: re.Pattern[str], text: str) -> Decimal:
    match = pattern.search(text)
    if not match:
        return Decimal("0")
    return as_decimal(match.group("value"))


def _split_segments(text: str) -> list[str]:
    return [segment.strip() for segment in re.split(r"[,;\n]+", text) if segment.strip()]


def _infer_category(description: str, catalog: PriceCatalog) -> ItemCategory:
    rate = catalog.find(description)
    if rate:
        return rate.category

    lowered = description.casefold()
    if any(hint in lowered for hint in LABOR_HINTS):
        return ItemCategory.LABOR
    if any(hint in lowered for hint in MATERIAL_HINTS):
        return ItemCategory.MATERIAL
    return ItemCategory.OTHER


def _default_price(description: str, catalog: PriceCatalog) -> Decimal:
    rate = catalog.find(description)
    if rate is None:
        raise ValueError(f"Set a unit price for '{description}' or add it to the price catalog")
    return rate.unit_price


def parse_estimate_request(
    text: str,
    *,
    project_name: str = "Quick estimate",
    catalog: PriceCatalog | None = None,
) -> Estimate:
    """Parse a compact natural-language request into an Estimate.

    The parser intentionally handles a narrow, predictable MVP format:
    "description quantity unit по unit_price, наценка N%".
    If a unit price is omitted, it tries the default catalog.
    """

    if not text.strip():
        raise ValueError("estimate request is empty")

    price_catalog = catalog or PriceCatalog()
    estimate = Estimate(
        project_name=project_name,
        markup_percent=_extract_percent(MARKUP_RE, text),
        tax_percent=_extract_percent(TAX_RE, text),
    )

    for segment in _split_segments(text):
        if MARKUP_RE.search(segment) or TAX_RE.search(segment):
            continue

        match = LINE_RE.search(segment)
        if not match:
            continue

        description = match.group("description").strip(" :-") or "line item"
        quantity = as_decimal(match.group("quantity"))
        unit = normalize_unit(match.group("unit"))
        unit_price = (
            as_decimal(match.group("unit_price"))
            if match.group("unit_price")
            else _default_price(description, price_catalog)
        )
        estimate.add_item(
            LineItem(
                description=description,
                quantity=quantity,
                unit=unit,
                unit_price=unit_price,
                category=_infer_category(description, price_catalog),
            )
        )

    if not estimate.line_items:
        raise ValueError("no estimate line items found")

    return estimate
