#!/usr/bin/env python3
"""Build a SQLite database from processed CSV exports."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "processed-csvs"
DEFAULT_DB_PATH = CSV_DIR / "oic-data.sqlite"

ORDERS_CSV = CSV_DIR / "orders.csv"
ATTACHMENTS_CSV = CSV_DIR / "attachments.csv"
MISSING_CSV = CSV_DIR / "missing-oic-pc-numbers.csv"


def normalize_text(text: str, mode: str) -> str:
    if mode == "preserve":
        return text

    stripped = text.strip()
    if mode == "strip":
        return stripped
    if mode == "collapse":
        return " ".join(stripped.split())
    if mode == "remove":
        return re.sub(r"\s+", "", text)

    raise ValueError(f"Unsupported whitespace mode: {mode}")


def load_orders(cur: sqlite3.Cursor, whitespace_mode: str) -> None:
    with ORDERS_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                """
                INSERT INTO orders (
                    pc_number,
                    html_hash,
                    attachments,
                    date,
                    chapter,
                    bill,
                    department,
                    act,
                    subject,
                    precis,
                    registration,
                    registration_type,
                    registration_id,
                    registration_publication_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["pcNumber"],
                    row["htmlHash"],
                    row["attachments"],
                    row["date"],
                    row["chapter"],
                    row["bill"],
                    normalize_text(row["department"], whitespace_mode),
                    normalize_text(row["act"], whitespace_mode),
                    normalize_text(row["subject"], whitespace_mode),
                    normalize_text(row["precis"], whitespace_mode),
                    normalize_text(row["registration"], whitespace_mode),
                    normalize_text(row["registration_type"], whitespace_mode),
                    normalize_text(row["registration_id"], whitespace_mode),
                    normalize_text(row["registration_publication_date"], whitespace_mode),
                ),
            )

            parsed_attachments = json.loads(row["attachments"] or "[]")
            if isinstance(parsed_attachments, (str, int)):
                attachment_ids = [parsed_attachments]
            elif isinstance(parsed_attachments, list):
                attachment_ids = parsed_attachments
            else:
                attachment_ids = []

            for attachment_id in attachment_ids:
                if str(attachment_id).strip() == "":
                    continue
                cur.execute(
                    "INSERT OR IGNORE INTO order_attachments (pc_number, attachment_id) VALUES (?, ?)",
                    (row["pcNumber"], int(attachment_id)),
                )


def load_attachments(cur: sqlite3.Cursor, whitespace_mode: str) -> None:
    with ATTACHMENTS_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO attachments (id, attachment_text) VALUES (?, ?)",
                (
                    int(row["id"]),
                    normalize_text(row["attachmentText"], whitespace_mode),
                ),
            )


def load_missing(cur: sqlite3.Cursor) -> None:
    with MISSING_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO missing_oic_pc_numbers (pc_number) VALUES (?)",
                (row["pc_number"],),
            )


def initialize_schema(cur: sqlite3.Cursor, create_secondary_indexes: bool) -> None:
    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE orders (
            pc_number TEXT PRIMARY KEY,
            html_hash TEXT,
            attachments TEXT,
            date TEXT,
            chapter TEXT,
            bill TEXT,
            department TEXT,
            act TEXT,
            subject TEXT,
            precis TEXT,
            registration TEXT,
            registration_type TEXT,
            registration_id TEXT,
            registration_publication_date TEXT
        );

        CREATE TABLE attachments (
            id INTEGER PRIMARY KEY,
            attachment_text TEXT
        );

        CREATE TABLE order_attachments (
            pc_number TEXT NOT NULL,
            attachment_id INTEGER NOT NULL,
            PRIMARY KEY (pc_number, attachment_id),
            FOREIGN KEY (pc_number) REFERENCES orders(pc_number) ON DELETE CASCADE
        );

        CREATE VIEW order_attachments_resolved AS
        SELECT
            oa.pc_number,
            oa.attachment_id,
            a.id IS NOT NULL AS attachment_exists
        FROM order_attachments oa
        LEFT JOIN attachments a ON a.id = oa.attachment_id;

        CREATE TABLE missing_oic_pc_numbers (
            pc_number TEXT PRIMARY KEY
        );
        """
    )
    if create_secondary_indexes:
        cur.executescript(
            """
            CREATE INDEX idx_orders_date ON orders(date);
            CREATE INDEX idx_order_attachments_attachment_id ON order_attachments(attachment_id);
            """
        )


def build_database(
    db_path: Path,
    order_whitespace: str,
    attachment_whitespace: str,
    create_secondary_indexes: bool,
) -> None:
    csv.field_size_limit(10_000_000)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode = OFF")
        cur.execute("PRAGMA synchronous = OFF")
        initialize_schema(cur, create_secondary_indexes)
        load_attachments(cur, attachment_whitespace)
        load_orders(cur, order_whitespace)
        load_missing(cur)
        conn.commit()
        cur.execute("VACUUM")
        conn.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"Output SQLite path (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--order-whitespace",
        choices=["preserve", "strip", "collapse", "remove"],
        default="strip",
        help=(
            "How to normalize order text whitespace: "
            "preserve, strip (default; trim ends), collapse (single-space runs), "
            "or remove (delete all whitespace)."
        ),
    )
    parser.add_argument(
        "--attachment-whitespace",
        choices=["preserve", "strip", "collapse", "remove"],
        default="strip",
        help=(
            "How to normalize attachment_text whitespace: "
            "preserve, strip (default; trim ends), collapse (single-space runs), "
            "or remove (delete all whitespace)."
        ),
    )
    parser.add_argument(
        "--no-secondary-indexes",
        action="store_true",
        help="Skip non-primary-key indexes to reduce database size.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_database(
        args.db_path,
        args.order_whitespace,
        args.attachment_whitespace,
        create_secondary_indexes=not args.no_secondary_indexes,
    )


if __name__ == "__main__":
    main()
