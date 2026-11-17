"""
main.py - Entry point for Student Expense Tracker
Module: Data Centric Programming (TU850 / Year 2) - TU Dublin
Author: Winnie Tan

Run this file to:
1. Initialize the SQLite database and verify all data records
2. Automatically generate the latest matplotlib analytical charts
3. Launch the interactive Tkinter GUI application
"""

import os
import sys

# Ensure src/ is in the module search path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database import load_csv_to_db, query_summary_statistics, DEFAULT_DB_PATH
from analysis import run_full_analysis
from app import ExpenseTrackerApp


def main():
    print("=" * 60)
    print("  Student Expense Tracker — TU Dublin (TU850)")
    print("  Author: Winnie Tan")
    print("=" * 60)

    # 1. Initialize SQLite Database from CSV if not already created
    if not os.path.exists(DEFAULT_DB_PATH):
        print("\n[1/3] Initializing SQLite database from data/expenses.csv...")
        count = load_csv_to_db()
        print(f"      -> Successfully imported {count} records into expenses.db.")
    else:
        print("\n[1/3] SQLite database detected. Verifying integrity...")

    stats = query_summary_statistics()
    print(f"      -> Total records in DB: {stats['total_records']}")
    print(f"      -> Total tracked spend: €{stats['total_spend']:,.2f}")

    # 2. Generate Matplotlib Charts
    print("\n[2/3] Generating analytical visualizations...")
    run_full_analysis()

    # 3. Launch Interactive Tkinter GUI
    print("\n[3/3] Launching Tkinter GUI application...")
    print("      (Close the application window to exit)")
    app = ExpenseTrackerApp()
    app.mainloop()
    print("\nApplication closed gracefully. Goodbye!")


if __name__ == "__main__":
    main()
