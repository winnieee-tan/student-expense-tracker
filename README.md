# 💶 Daily Expense Tracker for an International Student in Ireland

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Data](https://img.shields.io/badge/Dataset-Human--Made%20Data-10B981?style=for-the-badge)
![TU Dublin](https://img.shields.io/badge/TU%20Dublin-Data%20Centric%20Programming-003366?style=for-the-badge)

* **Module**: DATA2005 Data-Centric Programming (TU850 / Year 2)  
* **Institution**: Technological University Dublin (TU Dublin)  
* **Lecturer**: Dr Bryan Duggan  
* **Author**: Winnie Tan (Year 2 BSc in Data Science and Artificial Intelligence)  
* **Project Topic**: Human Made Data — Tracking Daily Living Expenses as an International Student in Dublin, Ireland  

---

## 📌 Project Proposal & Topic Overview

Moving to Dublin, Ireland as an international university student from Malaysia brings significant new financial responsibilities. Managing accommodation rent, groceries, transportation, mobile plans, utilities, and discretionary living requires careful budgeting, currency conversion awareness, and disciplined financial tracking.

The purpose of this project is to collect, observe, and manually measure an authentic, primary dataset of my daily expenses across the semester, and subsequently design:
1. A structured **SQLite relational database** to store and manage the records.
2. Exploratory data analysis using **pandas** and **matplotlib** to answer core financial questions.
3. An interactive **Tkinter desktop GUI** to view, filter, and record expenses.

---

## 📊 Data Collection & Measurement Plan

### Authenticity & Ethical Statement
* In strict accordance with the assignment guidelines, **100% of the data recorded in this repository is measured, counted, and observed directly by me**.
* **Zero synthetic data or GenAI** is used to generate or augment records.
* Data is recorded daily from banking app transactions (**Wise**, **AIB Bank**, and **Revolut**) and physical merchant receipts.

### Column Headings & Data Dictionary

The dataset is recorded in `data/expenses.csv` with the following 8 attributes:

| Column Name | Data Type | Unit / Example | Description |
| :--- | :--- | :--- | :--- |
| `Date` | Date | `2026-09-16` | The date of the transaction (ISO format YYYY-MM-DD). |
| `Item` | String | `Groceries (Tesco)` | Detailed description of the goods or services purchased. |
| `Category` | String | `Food & Groceries` | Category: *Personal & Household*, *Food & Groceries*, *Eating Out & Drinks*, *Entertainment & Leisure*, *Transport*, *Study & Supplies*. |
| `Amount` | Float | `17.05` | Transaction cost in Euros (€ EUR). |
| `Payment_Method` | String | `Wise` | Method used to complete payment (*Wise*, *AIB Bank*, *Revolut*). |
| `Essential` | String | `Y` | Binary classification: **Y** (Need / Essential) or **N** (Want / Discretionary). |
| `Location` | String | `Tesco Superstore` | Merchant name or location of the transaction. |
| `Day_Type` | String | `Weekday` | Day classification (*Weekday* vs *Weekend*). |

---

## ❓ Research Questions

Through this data collection and subsequent analysis, I aim to answer the following research questions:

1. **Where does most of my money go?**  
   *Which categories represent the highest proportion of expenditure (fixed accommodation overheads vs. everyday variable living)?*

2. **How much do I spend on average each day?**  
   *What is my realistic daily living burn rate in Dublin (both including and excluding fixed rent)?*

3. **Do I spend more money on needs or wants?**  
   *What percentage of my budget is allocated to non-negotiable essentials versus discretionary leisure?*

4. **Do my spending habits differ between weekdays and weekends?**  
   *Are weekends characterized by higher transaction frequency or higher average spend?*

5. **Which payment methods do I rely on most?**  
   *How does my reliance on multi-currency cards (Wise) compare to local Irish banking (AIB) and digital fintech (Revolut)?*

---

## 🗺️ Project Roadmap & Next Steps

- [x] **Step 1**: Project Proposal & Topic Definition.
- [x] **Step 2**: Data schema design and initial dataset recording in `data/expenses.csv`.
- [ ] **Step 3**: Database Design — SQLite schema creation, data types, and SQL aggregate queries (`GROUP BY`, `ORDER BY`, `WHERE`, `AVG`, `COUNT`).
- [ ] **Step 4**: Data Analysis — Implement pandas queries and generate statistical visualizations in matplotlib.
- [ ] **Step 5**: Interactive Application — Develop Tkinter GUI for viewing, filtering, and adding expenses.
- [ ] **Step 6**: Final Report & Live In-Class Demonstration.

---

## 📂 Repository Structure (Current)

```
student-expense-tracker/
├── data/
│   └── expenses.csv       # Human-made expense records
├── README.md              # Project proposal and research questions
└── .gitignore             # Git ignore configuration
```

---

<p align="left">
  <b>Author</b>: Winnie Tan<br/>
  Year 2 BSc in Data Science & Artificial Intelligence<br/>
  Technological University Dublin (TU Dublin)<br/>
  <a href="https://www.linkedin.com/in/winnie-tan-3413183a6">LinkedIn Profile</a> • <a href="https://github.com/winnieee-tan">GitHub Profile</a>
</p>
