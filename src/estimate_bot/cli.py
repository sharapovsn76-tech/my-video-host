"""Command line interface for quick estimate checks."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal

from estimate_bot.parser import parse_estimate_request


def _format_decimal(value: Decimal) -> str:
    return f"{value:.2f}"


def render_text(estimate) -> str:
    lines = [f"Estimate: {estimate.project_name}"]
    for item in estimate.line_items:
        lines.append(
            "- "
            f"{item.description}: {item.billable_quantity:g} {item.unit} "
            f"x {_format_decimal(item.unit_price)} = {_format_decimal(item.subtotal)}"
        )
    lines.append(f"Direct total: {_format_decimal(estimate.direct_total)}")
    if estimate.markup_percent:
        lines.append(f"Markup {estimate.markup_percent:g}%: {_format_decimal(estimate.markup_amount)}")
    if estimate.tax_percent:
        lines.append(f"Tax {estimate.tax_percent:g}%: {_format_decimal(estimate.tax_amount)}")
    lines.append(f"Grand total: {_format_decimal(estimate.grand_total)}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse and calculate a construction estimate request.")
    parser.add_argument("request", help="Estimate request text")
    parser.add_argument("--project", default="Quick estimate", help="Project name")
    parser.add_argument("--json", action="store_true", help="Print structured JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    estimate = parse_estimate_request(args.request, project_name=args.project)
    if args.json:
        print(json.dumps(estimate.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(render_text(estimate))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
