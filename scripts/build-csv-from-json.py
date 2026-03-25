#!/usr/bin/env python3
"""Build CSV exports from scraped JSON files."""

from __future__ import annotations

import csv
import gzip
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORDER_TABLES_DIR = ROOT / "order-tables"
ATTACHMENTS_DIR = ROOT / "attachments"
CSV_DIR = ROOT / "processed-csvs"

ORDER_FIELDS = [
    "pcNumber",
    "htmlHash",
    "attachments",
    "date",
    "chapter",
    "bill",
    "department",
    "act",
    "subject",
    "precis",
    "registration",
    "registration_type",
    "registration_id",
    "registration_publication_date",
]


def load_json_rows(directory: Path) -> list[dict]:
    rows: list[dict] = []

    for path in sorted(directory.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            rows.append(json.load(f))

    return rows


def stringify_attachments(value: object) -> str:
    if value in ("", None):
        return "[]"

    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    if isinstance(value, (str, int, float, bool)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    return "[]"


def write_orders_csv(orders: list[dict]) -> None:
    orders_csv = CSV_DIR / "orders.csv"
    orders_html_csv = CSV_DIR / "orders-html.csv"

    sorted_orders = sorted(orders, key=lambda row: row.get("pcNumber", ""))

    with orders_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=ORDER_FIELDS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()

        for order in sorted_orders:
            row = {field: order.get(field, "") for field in ORDER_FIELDS}
            row["attachments"] = stringify_attachments(order.get("attachments"))
            writer.writerow(row)

    with orders_html_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["pcNumber", "html"],
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()

        for order in sorted_orders:
            writer.writerow(
                {
                    "pcNumber": order.get("pcNumber", ""),
                    "html": order.get("html", ""),
                }
            )


def attachment_sort_key(row: dict) -> tuple[int, str]:
    raw_id = str(row.get("id", "")).strip()
    if raw_id.isdigit():
        return (int(raw_id), raw_id)
    return (10**18, raw_id)


def write_attachments_csv(attachments: list[dict]) -> None:
    attachments_csv = CSV_DIR / "attachments.csv"
    attachments_html_csv_gz = CSV_DIR / "attachments-html.csv.gz"

    sorted_attachments = sorted(attachments, key=attachment_sort_key)

    with attachments_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "attachmentText"],
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()

        for attachment in sorted_attachments:
            writer.writerow(
                {
                    "id": attachment.get("id", ""),
                    "attachmentText": attachment.get("attachmentText", ""),
                }
            )

    with attachments_html_csv_gz.open("wb") as raw_f:
        with gzip.GzipFile(fileobj=raw_f, mode="wb", compresslevel=9, mtime=0) as gz_f:
            with io.TextIOWrapper(gz_f, encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=["id", "attachmentHtml"],
                    extrasaction="ignore",
                    lineterminator="\n",
                )
                writer.writeheader()

                for attachment in sorted_attachments:
                    writer.writerow(
                        {
                            "id": attachment.get("id", ""),
                            "attachmentHtml": attachment.get("attachmentHtml", ""),
                        }
                    )


def main() -> None:
    csv.field_size_limit(10_000_000)
    CSV_DIR.mkdir(parents=True, exist_ok=True)

    write_orders_csv(load_json_rows(ORDER_TABLES_DIR))
    write_attachments_csv(load_json_rows(ATTACHMENTS_DIR))


if __name__ == "__main__":
    main()
