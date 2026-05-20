# Construction Estimate Bot

MVP foundation for a bot that prepares construction estimates, calculates
material quantities, and totals material/labor costs.

The repository currently focuses on the calculation core and a small command
line interface. Chat integrations (Telegram, web chat, CRM, etc.) can be added
on top of this core without changing the estimating rules.

## What is included

- Estimate data model with line items, markup, tax, and grand totals.
- Default price catalog for common residential renovation work.
- Rule-based parser for short Russian/English estimate requests.
- Material helpers for paint, tile, and drywall quantities.
- CLI for quick local checks.
- Unit tests built on Python's standard `unittest`.

## Quick start

```bash
python3 -m pip install -e .
estimate-bot "плитка 25 м2 по 1200 руб/м2, работа 25 м2 по 1800 руб/м2, наценка 15%"
```

Run tests:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Example output

```text
Estimate: Quick estimate
- плитка: 25 м2 x 1200.00 = 30000.00
- работа: 25 м2 x 1800.00 = 45000.00
Direct total: 75000.00
Markup 15%: 11250.00
Grand total: 86250.00
```

## Roadmap

1. Add a real bot channel (Telegram is usually the fastest first step).
2. Store estimates and project assumptions in SQLite/PostgreSQL.
3. Add PDF/Excel export for client-facing commercial proposals.
4. Expand the price catalog by trade, region, complexity, and contractor rates.
5. Add document/photo intake for extracting quantities from plans and notes.