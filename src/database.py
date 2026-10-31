"""
database.py - SQLite Database Management for Student Expense Tracker
Module: Data Centric Programming (TU850 / Year 2) - TU Dublin
Author: Winnie Tan

Handles:
- SQLite schema initialization with proper constraints and types
- Data cleaning, validation, and automated CSV import
- Complex analytical SQL queries (GROUP BY, ORDER BY, WHERE, AVG, COUNT)
- CRUD operations for interactive Tkinter GUI
"""

import sqlite3
import csv
import os
from datetime import datetime


DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "expenses.db")
DEFAULT_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "expenses.csv")


def get_connection(db_path=DEFAULT_DB_PATH):
    """Establishes a connection to the SQLite database with row factory."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path=DEFAULT_DB_PATH):
    """Creates the expenses table with appropriate data types and integrity constraints."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                item TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount >= 0),
                payment_method TEXT NOT NULL,
                essential TEXT NOT NULL CHECK(essential IN ('Y', 'N')),
                location TEXT DEFAULT 'Dublin',
                day_type TEXT NOT NULL CHECK(day_type IN ('Weekday', 'Weekend')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Index on date and category for fast querying and filtering
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_essential ON expenses(essential)")
        conn.commit()


def clean_amount(val):
    """Cleans currency strings like '€1,156.00' or 1156.00 into standard float."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).replace("€", "").replace(",", "").strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0


def clean_date(val):
    """Standardizes dates into ISO YYYY-MM-DD for reliable SQL date sorting."""
    if not val:
        return datetime.today().strftime("%Y-%m-%d")
    val_str = str(val).strip()
    # Try YYYY-MM-DD
    try:
        dt = datetime.strptime(val_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    # Try DD/MM/YYYY
    try:
        dt = datetime.strptime(val_str, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    return val_str


def load_csv_to_db(csv_path=DEFAULT_CSV_PATH, db_path=DEFAULT_DB_PATH, clear_existing=True):
    """Loads CSV dataset into SQLite database with full data validation and type casting."""
    init_database(db_path)
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")

    inserted_count = 0
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if clear_existing:
            cursor.execute("DELETE FROM expenses")

        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            # Normalize column names by lowercasing and stripping
            for row in reader:
                cleaned_row = {k.strip().lower().replace(" ", "_"): v for k, v in row.items() if k}

                date_val = clean_date(cleaned_row.get("date"))
                item_val = cleaned_row.get("item", "Unknown").strip()
                cat_val = cleaned_row.get("category", "Other").strip()
                amount_val = clean_amount(cleaned_row.get("amount") or cleaned_row.get("amount_euro"))
                payment_val = cleaned_row.get("payment_method", "Other").strip()
                
                # Essential normalization
                ess_val = cleaned_row.get("essential", "Y").strip().upper()
                if ess_val not in ("Y", "N"):
                    ess_val = "Y" if "need" in ess_val.lower() or "yes" in ess_val.lower() else "N"

                location_val = cleaned_row.get("location", "Dublin").strip()

                # Day type calculation/normalization
                day_type_val = cleaned_row.get("day_type", "").strip().capitalize()
                if day_type_val not in ("Weekday", "Weekend"):
                    try:
                        dt = datetime.strptime(date_val, "%Y-%m-%d")
                        day_type_val = "Weekend" if dt.weekday() >= 5 else "Weekday"
                    except ValueError:
                        day_type_val = "Weekday"

                cursor.execute("""
                    INSERT INTO expenses (date, item, category, amount, payment_method, essential, location, day_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (date_val, item_val, cat_val, amount_val, payment_val, ess_val, location_val, day_type_val))
                inserted_count += 1

        conn.commit()
    return inserted_count


def add_expense(date, item, category, amount, payment_method, essential, location, day_type, db_path=DEFAULT_DB_PATH):
    """Inserts a single expense record (Used by Tkinter GUI and CRUD operations)."""
    clean_dt = clean_date(date)
    clean_amt = clean_amount(amount)
    
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO expenses (date, item, category, amount, payment_method, essential, location, day_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (clean_dt, item.strip(), category.strip(), clean_amt, payment_method.strip(), essential.strip().upper(), location.strip(), day_type.strip()))
        conn.commit()
        return cursor.lastrowid


def delete_expense(expense_id, db_path=DEFAULT_DB_PATH):
    """Deletes an expense record by primary key id."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        return cursor.rowcount > 0


# -------------------------------------------------------------
# Rubric Analytical SQL Queries (GROUP BY, ORDER BY, WHERE, AVG, COUNT)
# -------------------------------------------------------------

def query_all_expenses(order_by="date DESC", db_path=DEFAULT_DB_PATH):
    """Retrieves all expenses with dynamic ORDER BY."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM expenses ORDER BY {order_by}")
        return cursor.fetchall()


def query_spending_by_category(db_path=DEFAULT_DB_PATH):
    """Demonstrates GROUP BY, COUNT, SUM, AVG, and ORDER BY."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                category,
                COUNT(*) AS transaction_count,
                ROUND(SUM(amount), 2) AS total_amount,
                ROUND(AVG(amount), 2) AS average_amount,
                ROUND((SUM(amount) * 100.0 / (SELECT SUM(amount) FROM expenses)), 2) AS percentage_of_total
            FROM expenses
            GROUP BY category
            ORDER BY total_amount DESC
        """)
        return cursor.fetchall()


def query_needs_vs_wants(db_path=DEFAULT_DB_PATH):
    """Demonstrates WHERE, GROUP BY, and AVG to compare Essential vs Discretionary spend."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                CASE WHEN essential = 'Y' THEN 'Needs (Essential)' ELSE 'Wants (Discretionary)' END AS spending_type,
                COUNT(*) AS transaction_count,
                ROUND(SUM(amount), 2) AS total_amount,
                ROUND(AVG(amount), 2) AS average_transaction
            FROM expenses
            GROUP BY essential
            ORDER BY total_amount DESC
        """)
        return cursor.fetchall()


def query_weekday_vs_weekend(db_path=DEFAULT_DB_PATH):
    """Demonstrates GROUP BY and AVG across Day Type."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                day_type,
                COUNT(*) AS transaction_count,
                ROUND(SUM(amount), 2) AS total_amount,
                ROUND(AVG(amount), 2) AS avg_per_transaction
            FROM expenses
            GROUP BY day_type
            ORDER BY total_amount DESC
        """)
        return cursor.fetchall()


def query_top_expenses(limit=5, db_path=DEFAULT_DB_PATH):
    """Demonstrates WHERE and ORDER BY to inspect largest purchases."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, date, item, category, amount, payment_method, location
            FROM expenses
            ORDER BY amount DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()


def query_summary_statistics(db_path=DEFAULT_DB_PATH):
    """Calculates overall metrics using COUNT, SUM, AVG, MIN, MAX."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) AS total_records,
                ROUND(SUM(amount), 2) AS total_spend,
                ROUND(AVG(amount), 2) AS avg_spend,
                ROUND(MIN(amount), 2) AS min_spend,
                ROUND(MAX(amount), 2) AS max_spend,
                COUNT(DISTINCT category) AS total_categories,
                MIN(date) AS start_date,
                MAX(date) AS end_date
            FROM expenses
        """)
        return dict(cursor.fetchone())


if __name__ == "__main__":
    count = load_csv_to_db()
    print(f"Successfully initialized database and inserted {count} records.")
    stats = query_summary_statistics()
    print("Summary Statistics:", stats)
