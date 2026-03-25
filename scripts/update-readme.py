#!/usr/bin/env python3
"""Update dynamic README sections from scraped OIC JSON data."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"
ORDER_TABLES_DIR = ROOT / "order-tables"

MAX_RECENT_ORDERS = 10
MAX_ACT_SERIES = 6


@dataclass
class OrderRow:
    pc_number: str
    date: datetime | None
    date_text: str
    department: str
    act: str
    subject: str


def parse_date(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None


def clean_text(value: str, fallback: str = "") -> str:
    normalized = " ".join((value or "").split())
    return normalized or fallback


def load_orders() -> list[OrderRow]:
    orders: list[OrderRow] = []

    for path in sorted(ORDER_TABLES_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        date_text = raw.get("date", "") or ""
        orders.append(
            OrderRow(
                pc_number=raw.get("pcNumber", path.stem),
                date=parse_date(date_text),
                date_text=date_text,
                department=clean_text(raw.get("department", ""), "Not listed"),
                act=clean_text(raw.get("act", ""), "No Act Listed"),
                subject=clean_text(raw.get("subject", ""), "No subject listed"),
            )
        )

    return orders


def replace_block(readme: str, marker: str, content: str) -> str:
    start_marker = f"<!-- {marker}:START -->"
    end_marker = f"<!-- {marker}:END -->"
    start = readme.find(start_marker)
    end = readme.find(end_marker)

    if start == -1 or end == -1 or end < start:
        raise ValueError(f"Missing README marker block: {marker}")

    block_start = start + len(start_marker)
    return readme[:block_start] + "\n" + content.rstrip() + "\n" + readme[end:]


def render_status_block(orders: list[OrderRow]) -> str:
    dated_orders = [order for order in orders if order.date is not None]
    latest_order_date = max(order.date for order in dated_orders)
    last_checked = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

    return "\n".join(
        [
            f"**Latest OIC date:** {latest_order_date.strftime('%Y-%m-%d')}",
            f"**Last checked:** {last_checked}",
        ]
    )


def render_recent_orders_table(orders: list[OrderRow]) -> str:
    sorted_orders = sorted(
        orders,
        key=lambda order: (
            order.date or datetime.min,
            order.pc_number,
        ),
        reverse=True,
    )

    lines = [
        "| Date | PC Number | Department | Act | Subject |",
        "| --- | --- | --- | --- | --- |",
    ]

    for order in sorted_orders[:MAX_RECENT_ORDERS]:
        lines.append(
            "| {date} | {pc} | {department} | {act} | {subject} |".format(
                date=order.date_text or "Unknown",
                pc=order.pc_number,
                department=order.department.replace("|", "\\|"),
                act=order.act.replace("|", "\\|"),
                subject=order.subject.replace("|", "\\|"),
            )
        )

    return "\n".join(lines)


def render_year_chart(orders: list[OrderRow]) -> str:
    counts: Counter[int] = Counter()
    for order in orders:
        if order.date is not None:
            counts[order.date.year] += 1

    years = sorted(counts)
    year_labels = ", ".join(
        f'"{year}"' if year % 5 == 0 else '" "'
        for year in years
    )
    values = ", ".join(str(counts[year]) for year in years)
    max_count = max(counts.values(), default=0)

    return "\n".join(
        [
            "```mermaid",
            "xychart-beta",
            '    title "Orders in Council by Year"',
            f"    x-axis [{year_labels}]",
            f'    y-axis "Orders" 0 --> {max_count}',
            f"    line [{values}]",
            "```",
        ]
    )


def iter_last_n_months(anchor: datetime, months: int) -> list[str]:
    year = anchor.year
    month = anchor.month
    labels: list[str] = []

    for offset in range(months - 1, -1, -1):
        cur_month = month - offset
        cur_year = year
        while cur_month <= 0:
            cur_month += 12
            cur_year -= 1
        labels.append(f"{cur_year:04d}-{cur_month:02d}")

    return labels


def render_monthly_act_chart(orders: list[OrderRow]) -> str:
    dated_orders = [order for order in orders if order.date is not None]
    latest_order_date = max(order.date for order in dated_orders)
    month_labels = iter_last_n_months(latest_order_date, 12)

    per_act: dict[str, Counter[str]] = defaultdict(Counter)
    for order in dated_orders:
        month_key = order.date.strftime("%Y-%m")
        if month_key in month_labels:
            per_act[order.act][month_key] += 1

    top_acts = [
        act
        for act, _count in sorted(
            (
                (act, sum(month_counts.values()))
                for act, month_counts in per_act.items()
            ),
            key=lambda item: (-item[1], item[0]),
        )[:MAX_ACT_SERIES]
    ]

    other_counts: Counter[str] = Counter()
    for act, month_counts in per_act.items():
        if act not in top_acts:
            other_counts.update(month_counts)

    series: list[tuple[str, list[int]]] = []
    for act in top_acts:
        series.append((act, [per_act[act][month] for month in month_labels]))
    if sum(other_counts.values()) > 0:
        series.append(("Other", [other_counts[month] for month in month_labels]))

    all_values = [value for _label, values in series for value in values]
    max_count = max(all_values, default=0)

    lines = [
        "Series order: " + "; ".join(
            f"{index + 1}. {label}" for index, (label, _values) in enumerate(series)
        ),
        "",
        "```mermaid",
        "xychart-beta",
        '    title "Monthly Order Counts by Act (Latest 12 Months)"',
        f"    x-axis [{', '.join(f'\"{month}\"' for month in month_labels)}]",
        f'    y-axis "Orders" 0 --> {max_count}',
    ]

    for _label, values in series:
        lines.append(f"    line [{', '.join(str(value) for value in values)}]")

    lines.append("```")
    return "\n".join(lines)


def main() -> None:
    orders = load_orders()
    readme = README_PATH.read_text(encoding="utf-8")

    readme = replace_block(readme, "STATUS", render_status_block(orders))
    readme = replace_block(readme, "RECENT_ORDERS", render_recent_orders_table(orders))
    readme = replace_block(readme, "ORDERS_BY_YEAR", render_year_chart(orders))
    readme = replace_block(readme, "MONTHLY_ACT_CHART", render_monthly_act_chart(orders))

    README_PATH.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
