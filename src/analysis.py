"""
analysis.py - Exploratory Data Analysis & Visualizations
Module: Data Centric Programming (TU850 / Year 2) - TU Dublin
Author: Winnie Tan

Uses pandas and matplotlib to answer key research questions:
1. Category Spending: Where does most of the money go?
2. Needs vs. Wants: How much is spent on essentials compared to discretionary purchases?
3. Temporal Trends: How do weekday and weekend spending patterns compare?
4. Daily Spending & Cumulative Trajectory: What is the true daily living cost?
5. Payment Ecosystem: How are Wise, AIB Bank, and Revolut utilized?
"""

import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "expenses.db")
VIZ_DIR = os.path.join(BASE_DIR, "visualizations")


def setup_matplotlib_style():
    """Applies a clean, modern aesthetic for all presentation graphs."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
    plt.rcParams["axes.edgecolor"] = "#cccccc"
    plt.rcParams["axes.linewidth"] = 0.8


def load_dataframe_from_db(db_path=DB_PATH):
    """Loads expenses from SQLite into a pandas DataFrame with proper datetime indexing."""
    conn = sqlite3.connect(db_path)
    query = """
        SELECT id, date, item, category, amount, payment_method, essential, location, day_type
        FROM expenses
        ORDER BY date ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = pd.to_numeric(df["amount"])
    return df


def plot_category_spending(df, save_dir=VIZ_DIR):
    """Answers Research Question 1: Where does most of my money go?"""
    cat_summary = df.groupby("category")["amount"].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    colors = ["#38BDF8", "#3B82F6", "#6366F1", "#8B5CF6", "#EC4899", "#F59E0B"]
    
    bars = ax.barh(cat_summary.index, cat_summary.values, color=colors[:len(cat_summary)], edgecolor="none", height=0.6)

    # Format axis
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("€{x:,.0f}"))
    ax.set_title("Total Expenditure by Category (Aug – Oct 2026)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Total Amount (€ EUR)", fontsize=11, labelpad=10)
    ax.set_ylabel("Spending Category", fontsize=11, labelpad=10)

    # Add data labels at end of bars
    for bar in bars:
        width = bar.get_width()
        percentage = (width / cat_summary.sum()) * 100
        ax.text(width + (cat_summary.max() * 0.015), bar.get_y() + bar.get_height() / 2,
                f"€{width:,.2f} ({percentage:.1f}%)",
                va="center", ha="left", fontsize=9, fontweight="bold", color="#1F2937")

    ax.set_xlim(0, cat_summary.max() * 1.25)
    plt.tight_layout()
    output_path = os.path.join(save_dir, "category_spending.png")
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_needs_vs_wants(df, save_dir=VIZ_DIR):
    """Answers Research Question 3: How much do I spend on needs compared with wants?"""
    needs_summary = df.groupby("essential")["amount"].sum()
    labels = ["Discretionary (Wants)", "Essential (Needs)"]
    sizes = [needs_summary.get("N", 0), needs_summary.get("Y", 0)]
    colors = ["#F43F5E", "#10B981"]

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.1f%%", startangle=140,
        colors=colors, explode=(0.06, 0), pctdistance=0.75,
        textprops=dict(color="#1F2937", fontsize=11, fontweight="bold")
    )

    # Donut hole
    centre_circle = plt.Circle((0, 0), 0.55, fc='white')
    ax.add_artist(centre_circle)

    # Center total label
    total_val = sum(sizes)
    ax.text(0, 0, f"Total\n€{total_val:,.2f}", ha='center', va='center', fontsize=12, fontweight='bold', color='#111827')

    ax.set_title("Spending Breakdown: Needs (Essential) vs. Wants (Discretionary)", fontsize=13, fontweight="bold", pad=15)
    plt.tight_layout()
    output_path = os.path.join(save_dir, "needs_vs_wants.png")
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_weekday_vs_weekend(df, save_dir=VIZ_DIR):
    """Answers Research Question 4: Do spending patterns differ between weekdays and weekends?"""
    day_summary = df.groupby("day_type").agg(
        total_amount=("amount", "sum"),
        avg_amount=("amount", "mean"),
        count=("amount", "count")
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), dpi=300)

    # Total spend
    ax1.bar(day_summary.index, day_summary["total_amount"], color=["#3B82F6", "#8B5CF6"], width=0.45)
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("€{x:,.0f}"))
    ax1.set_title("Total Spending (€)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Total (€ EUR)")
    for i, v in enumerate(day_summary["total_amount"]):
        ax1.text(i, v + 50, f"€{v:,.2f}", ha="center", fontweight="bold", fontsize=9)
    ax1.set_ylim(0, day_summary["total_amount"].max() * 1.15)

    # Average per transaction
    ax2.bar(day_summary.index, day_summary["avg_amount"], color=["#06B6D4", "#EC4899"], width=0.45)
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter("€{x:,.0f}"))
    ax2.set_title("Average Transaction Amount (€)", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Average (€ EUR)")
    for i, v in enumerate(day_summary["avg_amount"]):
        ax2.text(i, v + 4, f"€{v:,.2f}", ha="center", fontweight="bold", fontsize=9)
    ax2.set_ylim(0, day_summary["avg_amount"].max() * 1.2)

    plt.suptitle("Weekday vs. Weekend Financial Comparison", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    output_path = os.path.join(save_dir, "weekday_vs_weekend.png")
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_cumulative_spending(df, save_dir=VIZ_DIR):
    """Answers Research Question 2: Daily expenditure trajectory and cumulative spending."""
    daily = df.groupby("date")["amount"].sum().reset_index()
    daily["cumulative"] = daily["amount"].cumsum()

    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    ax.plot(daily["date"], daily["cumulative"], marker="o", markersize=4, color="#2563EB", linewidth=2.2, label="Cumulative Spend (€)")
    ax.fill_between(daily["date"], daily["cumulative"], color="#3B82F6", alpha=0.15)

    # Highlight major milestone events (rent, laptop)
    rent_events = df[df["amount"] >= 1000]
    for _, row in rent_events.iterrows():
        ax.annotate("Accommodation Rent\n(€1,156)", xy=(row["date"], daily.loc[daily["date"] == row["date"], "cumulative"].values[0]),
                    xytext=(-30, 25), textcoords="offset points",
                    arrowprops=dict(arrowstyle="->", color="#DC2626", lw=1.2),
                    fontsize=8, fontweight="bold", color="#DC2626")

    laptop_event = df[df["item"].str.contains("Laptop", case=False, na=False)]
    if not laptop_event.empty:
        row = laptop_event.iloc[0]
        cum_val = daily.loc[daily["date"] == row["date"], "cumulative"].values[0]
        ax.annotate("DELL Laptop (€791)", xy=(row["date"], cum_val),
                    xytext=(-60, -35), textcoords="offset points",
                    arrowprops=dict(arrowstyle="->", color="#D97706", lw=1.2),
                    fontsize=8, fontweight="bold", color="#D97706")

    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("€{x:,.0f}"))
    ax.set_title("Cumulative Spending Trajectory Over Semester (Aug – Oct 2026)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=10, labelpad=8)
    ax.set_ylabel("Cumulative Spend (€ EUR)", fontsize=10, labelpad=8)
    plt.xticks(rotation=25)
    plt.tight_layout()
    output_path = os.path.join(save_dir, "cumulative_spending.png")
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_payment_methods(df, save_dir=VIZ_DIR):
    """Answers Research Question 5: Payment method distribution."""
    method_summary = df.groupby("payment_method")["amount"].agg(["sum", "count"]).sort_values(by="sum", ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    bars = ax.bar(method_summary.index, method_summary["sum"], color=["#10B981", "#6366F1", "#F59E0B"], width=0.45)
    
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("€{x:,.0f}"))
    ax.set_title("Expenditure by Payment Method (Wise, AIB Bank, Revolut)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Payment Provider", fontsize=10, labelpad=8)
    ax.set_ylabel("Total Spend (€ EUR)", fontsize=10, labelpad=8)

    for bar, count in zip(bars, method_summary["count"]):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 60,
                f"€{height:,.2f}\n({count} transactions)",
                ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1F2937")

    ax.set_ylim(0, method_summary["sum"].max() * 1.22)
    plt.tight_layout()
    output_path = os.path.join(save_dir, "payment_distribution.png")
    plt.savefig(output_path)
    plt.close()
    return output_path


def run_full_analysis():
    """Executes the complete analytical pipeline and saves all charts."""
    os.makedirs(VIZ_DIR, exist_ok=True)
    setup_matplotlib_style()
    df = load_dataframe_from_db()

    print(f"Loaded {len(df)} records for analysis.")
    p1 = plot_category_spending(df)
    p2 = plot_needs_vs_wants(df)
    p3 = plot_weekday_vs_weekend(df)
    p4 = plot_cumulative_spending(df)
    p5 = plot_payment_methods(df)

    print("All charts generated successfully:")
    for p in [p1, p2, p3, p4, p5]:
        print(f" - {p}")

    # Calculate executive metrics
    non_rent = df[~df["item"].str.contains("Rent", case=False)]
    total_days = (df["date"].max() - df["date"].min()).days + 1
    daily_avg_all = df["amount"].sum() / total_days
    daily_avg_living = non_rent["amount"].sum() / total_days

    print("\n--- Executive Summary ---")
    print(f"Total Period: {df['date'].min().strftime('%d %b %Y')} to {df['date'].max().strftime('%d %b %Y')} ({total_days} days)")
    print(f"Total Expenditure: €{df['amount'].sum():,.2f}")
    print(f"Daily Average (Including Rent/Laptop): €{daily_avg_all:,.2f}/day")
    print(f"Daily Living Average (Excluding Rent): €{daily_avg_living:,.2f}/day")
    print(f"Essential Spending Ratio: {(df[df['essential'] == 'Y']['amount'].sum() / df['amount'].sum()) * 100:.1f}%")


if __name__ == "__main__":
    run_full_analysis()
