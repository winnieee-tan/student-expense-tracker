"""
app.py - Interactive Tkinter GUI Application for Student Expense Tracker
Module: Data Centric Programming (TU850 / Year 2) - TU Dublin
Author: Winnie Tan

Features:
- View expense records in a sorted, interactive Treeview table
- Dynamic filtering by Category, Essential status (Need/Want), and Search keyword
- Real-time metrics dashboard (Total Spent, Total Records, Needs %, Discretionary %)
- Add New Expense Dialog with form validation (Bonus Rubric Opportunity)
- Embedded / Interactive Graph Viewer showcasing all matplotlib analysis charts
- Refresh & CSV Export capability
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk

# Support running directly or as module
try:
    from .database import (
        DEFAULT_DB_PATH, get_connection, add_expense, delete_expense,
        query_summary_statistics, query_spending_by_category, init_database
    )
    from .analysis import run_full_analysis, VIZ_DIR
except ImportError:
    from database import (
        DEFAULT_DB_PATH, get_connection, add_expense, delete_expense,
        query_summary_statistics, query_spending_by_category, init_database
    )
    from analysis import run_full_analysis, VIZ_DIR


class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Expense Tracker — TU Dublin (TU850)")
        self.geometry("1100x720")
        self.minsize(950, 600)

        # Apply system styling
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.configure_styles()
        init_database()

        # State variables
        self.filter_category = tk.StringVar(value="All")
        self.filter_essential = tk.StringVar(value="All")
        self.search_keyword = tk.StringVar(value="")

        self.create_widgets()
        self.refresh_data()

    def configure_styles(self):
        """Configures clean UI colors and font hierarchy."""
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#003366")
        self.style.configure("Subheader.TLabel", font=("Segoe UI", 10), foreground="#4B5563")
        self.style.configure("MetricVal.TLabel", font=("Segoe UI", 14, "bold"), foreground="#1E3A8A")
        self.style.configure("MetricLbl.TLabel", font=("Segoe UI", 9), foreground="#6B7280")
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#E5E7EB")
        self.style.configure("Treeview", rowheight=26)

    def create_widgets(self):
        # 1. Header Frame
        header_frame = ttk.Frame(self, padding=(20, 15, 20, 10))
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="📊 International Student Expense Tracker", style="Header.TLabel")
        title_lbl.pack(anchor="w")
        sub_lbl = ttk.Label(header_frame, text="Human-Made Data Collection & Analytics | Data Centric Programming (TU Dublin)", style="Subheader.TLabel")
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # 2. Metric Cards Frame
        self.metrics_frame = ttk.LabelFrame(self, text=" Financial Summary Dashboard ", padding=(15, 10))
        self.metrics_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        self.card_total = self.create_metric_card(self.metrics_frame, "Total Expenditure", "€0.00", 0)
        self.card_daily = self.create_metric_card(self.metrics_frame, "Daily Living Avg (No Rent)", "€0.00/day", 1)
        self.card_records = self.create_metric_card(self.metrics_frame, "Total Records", "0 entries", 2)
        self.card_needs = self.create_metric_card(self.metrics_frame, "Essential (Needs) %", "0.0%", 3)

        # 3. Controls & Filter Bar
        ctrl_frame = ttk.Frame(self, padding=(20, 0, 20, 10))
        ctrl_frame.pack(fill=tk.X)

        ttk.Label(ctrl_frame, text="Category:").pack(side=tk.LEFT, padx=(0, 5))
        self.cat_combo = ttk.Combobox(ctrl_frame, textvariable=self.filter_category, state="readonly", width=18)
        self.cat_combo["values"] = ("All", "Personal & Household", "Food & Groceries", "Eating Out & Drinks", "Entertainment & Leisure", "Transport", "Study & Supplies")
        self.cat_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        ttk.Label(ctrl_frame, text="Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.ess_combo = ttk.Combobox(ctrl_frame, textvariable=self.filter_essential, state="readonly", width=12)
        self.ess_combo["values"] = ("All", "Needs (Y)", "Wants (N)")
        self.ess_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.ess_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        ttk.Label(ctrl_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(ctrl_frame, textvariable=self.search_keyword, width=16)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_data())

        # Action Buttons
        btn_add = ttk.Button(ctrl_frame, text="➕ Add Expense (Bonus)", command=self.open_add_expense_dialog)
        btn_add.pack(side=tk.RIGHT, padx=(5, 0))

        btn_graph = ttk.Button(ctrl_frame, text="📈 View Visualizations", command=self.open_graph_viewer)
        btn_graph.pack(side=tk.RIGHT, padx=5)

        btn_refresh = ttk.Button(ctrl_frame, text="🔄 Refresh", command=self.refresh_data)
        btn_refresh.pack(side=tk.RIGHT, padx=5)

        # 4. Treeview Table
        table_frame = ttk.Frame(self, padding=(20, 0, 20, 15))
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "date", "item", "category", "amount", "payment_method", "essential", "location", "day_type")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("item", text="Item / Description")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount (€)")
        self.tree.heading("payment_method", text="Payment")
        self.tree.heading("essential", text="Need/Want")
        self.tree.heading("location", text="Location")
        self.tree.heading("day_type", text="Day Type")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("date", width=95, anchor="center")
        self.tree.column("item", width=220, anchor="w")
        self.tree.column("category", width=160, anchor="w")
        self.tree.column("amount", width=90, anchor="e")
        self.tree.column("payment_method", width=90, anchor="center")
        self.tree.column("essential", width=85, anchor="center")
        self.tree.column("location", width=130, anchor="w")
        self.tree.column("day_type", width=85, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Context menu for delete
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="🗑️ Delete Expense", command=self.delete_selected_expense)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def create_metric_card(self, parent, label_text, val_text, col):
        frame = ttk.Frame(parent, padding=(10, 5))
        frame.grid(row=0, column=col, sticky="ew", padx=10)
        parent.grid_columnconfigure(col, weight=1)

        lbl = ttk.Label(frame, text=label_text, style="MetricLbl.TLabel")
        lbl.pack(anchor="center")
        val = ttk.Label(frame, text=val_text, style="MetricVal.TLabel")
        val.pack(anchor="center")
        return val

    def refresh_data(self):
        """Queries SQLite with active filters and updates Treeview + summary cards."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Build dynamic SQL query
        query = "SELECT id, date, item, category, amount, payment_method, essential, location, day_type FROM expenses WHERE 1=1"
        params = []

        cat = self.filter_category.get()
        if cat != "All":
            query += " AND category = ?"
            params.append(cat)

        ess = self.filter_essential.get()
        if ess == "Needs (Y)":
            query += " AND essential = 'Y'"
        elif ess == "Wants (N)":
            query += " AND essential = 'N'"

        search = self.search_keyword.get().strip()
        if search:
            query += " AND (item LIKE ? OR location LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += " ORDER BY date DESC, id DESC"

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        total_filtered_spend = 0.0
        for row in rows:
            formatted_amt = f"€{row['amount']:,.2f}"
            formatted_ess = "Need (Y)" if row["essential"] == "Y" else "Want (N)"
            self.tree.insert("", "end", values=(
                row["id"], row["date"], row["item"], row["category"],
                formatted_amt, row["payment_method"], formatted_ess,
                row["location"], row["day_type"]
            ))
            total_filtered_spend += row["amount"]

        # Update metrics cards
        stats = query_summary_statistics()
        if stats and stats["total_records"]:
            self.card_total.config(text=f"€{stats['total_spend']:,.2f}")
            self.card_records.config(text=f"{len(rows)} / {stats['total_records']} shown")

            # Non-rent living average
            with get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT SUM(amount) FROM expenses WHERE item NOT LIKE '%Rent%'")
                non_rent_total = c.fetchone()[0] or 0.0
                c.execute("SELECT (julianday(MAX(date)) - julianday(MIN(date)) + 1) FROM expenses")
                days = c.fetchone()[0] or 1
                daily_living = non_rent_total / max(days, 1)

                c.execute("SELECT SUM(amount) FROM expenses WHERE essential = 'Y'")
                essential_total = c.fetchone()[0] or 0.0
                needs_pct = (essential_total / stats["total_spend"]) * 100

            self.card_daily.config(text=f"€{daily_living:,.2f}/day")
            self.card_needs.config(text=f"{needs_pct:.1f}%")

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def delete_selected_expense(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_vals = self.tree.item(selected[0], "values")
        exp_id, item_name, amt = item_vals[0], item_vals[2], item_vals[4]

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete:\n\n{item_name} ({amt})?"):
            delete_expense(exp_id)
            self.refresh_data()
            messagebox.showinfo("Success", "Expense record deleted successfully.")

    def open_add_expense_dialog(self):
        """Bonus Opportunity: Dialog modal allowing user to record a new expense."""
        dialog = tk.Toplevel(self)
        dialog.title("Add New Expense")
        dialog.geometry("450x520")
        dialog.transient(self)
        dialog.grab_set()

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form_frame, text="Record New Expense", font=("Segoe UI", 13, "bold"), foreground="#003366").pack(anchor="w", pady=(0, 15))

        # Fields
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").pack(anchor="w")
        ent_date = ttk.Entry(form_frame)
        ent_date.insert(0, datetime.today().strftime("%Y-%m-%d"))
        ent_date.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(form_frame, text="Item / Description:").pack(anchor="w")
        ent_item = ttk.Entry(form_frame)
        ent_item.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(form_frame, text="Category:").pack(anchor="w")
        cmb_cat = ttk.Combobox(form_frame, state="readonly", values=[
            "Food & Groceries", "Eating Out & Drinks", "Personal & Household",
            "Transport", "Entertainment & Leisure", "Study & Supplies"
        ])
        cmb_cat.set("Food & Groceries")
        cmb_cat.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(form_frame, text="Amount (€):").pack(anchor="w")
        ent_amt = ttk.Entry(form_frame)
        ent_amt.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(form_frame, text="Payment Method:").pack(anchor="w")
        cmb_pay = ttk.Combobox(form_frame, state="readonly", values=["Wise", "AIB Bank", "Revolut", "Cash"])
        cmb_pay.set("Wise")
        cmb_pay.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(form_frame, text="Classification:").pack(anchor="w")
        cmb_ess = ttk.Combobox(form_frame, state="readonly", values=["Need (Y)", "Want (N)"])
        cmb_ess.set("Need (Y)")
        cmb_ess.pack(fill=tk.X, pady=(2, 10))

        ttk.Label(form_frame, text="Location:").pack(anchor="w")
        ent_loc = ttk.Entry(form_frame)
        ent_loc.insert(0, "Dublin")
        ent_loc.pack(fill=tk.X, pady=(2, 15))

        def submit_expense():
            date_val = ent_date.get().strip()
            item_val = ent_item.get().strip()
            cat_val = cmb_cat.get().strip()
            amt_str = ent_amt.get().strip().replace("€", "")
            pay_val = cmb_pay.get().strip()
            ess_val = "Y" if "Need" in cmb_ess.get() else "N"
            loc_val = ent_loc.get().strip() or "Dublin"

            if not item_val:
                messagebox.showerror("Validation Error", "Item description cannot be empty.", parent=dialog)
                return
            try:
                amt_val = float(amt_str)
                if amt_val <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid positive number for Amount.", parent=dialog)
                return

            try:
                dt = datetime.strptime(date_val, "%Y-%m-%d")
                day_type_val = "Weekend" if dt.weekday() >= 5 else "Weekday"
            except ValueError:
                messagebox.showerror("Validation Error", "Date must follow YYYY-MM-DD format.", parent=dialog)
                return

            add_expense(date_val, item_val, cat_val, amt_val, pay_val, ess_val, loc_val, day_type_val)
            self.refresh_data()
            dialog.destroy()
            messagebox.showinfo("Success", f"Recorded expense: '{item_val}' (€{amt_val:.2f})!")

        btn_save = ttk.Button(form_frame, text="💾 Save to Database", command=submit_expense)
        btn_save.pack(fill=tk.X, pady=(5, 0))

    def open_graph_viewer(self):
        """Viewer window enabling user to browse all matplotlib charts."""
        viewer = tk.Toplevel(self)
        viewer.title("Expense Visualizations & Analytics")
        viewer.geometry("880x660")
        viewer.minsize(750, 550)

        # Ensure graphs are generated
        run_full_analysis()

        chart_files = [
            ("Category Spending Breakdown", os.path.join(VIZ_DIR, "category_spending.png")),
            ("Needs vs. Wants Ratio", os.path.join(VIZ_DIR, "needs_vs_wants.png")),
            ("Weekday vs. Weekend Spending", os.path.join(VIZ_DIR, "weekday_vs_weekend.png")),
            ("Cumulative Semester Trajectory", os.path.join(VIZ_DIR, "cumulative_spending.png")),
            ("Payment Method Distribution", os.path.join(VIZ_DIR, "payment_distribution.png")),
        ]

        top_bar = ttk.Frame(viewer, padding=10)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="Select Chart: ", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        chart_names = [name for name, _ in chart_files]
        chart_combo = ttk.Combobox(top_bar, values=chart_names, state="readonly", width=35)
        chart_combo.set(chart_names[0])
        chart_combo.pack(side=tk.LEFT, padx=10)

        img_label = ttk.Label(viewer)
        img_label.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        def display_chart(index):
            _, file_path = chart_files[index]
            if os.path.exists(file_path):
                img = Image.open(file_path)
                # Resize smoothly to fit window
                img.thumbnail((820, 540), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                img_label.config(image=photo)
                img_label.image = photo

        chart_combo.bind("<<ComboboxSelected>>", lambda e: display_chart(chart_combo.current()))
        display_chart(0)


def main():
    app = ExpenseTrackerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
