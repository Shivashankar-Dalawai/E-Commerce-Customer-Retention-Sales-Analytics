# 📊 End-to-End E-Commerce Customer Retention & Sales Analytics

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![Analytics](https://img.shields.io/badge/Analytics-RFM%20%26%20Cohort-success.svg)]()
[![Dashboard](https://img.shields.io/badge/Dashboard-Power%20BI%20%2F%20HTML5-F2C811.svg)]()

> A full-stack data analytics portfolio project demonstrating data extraction, automated data cleaning in Python, SQL window functions, customer cohort retention, RFM behavioral segmentation, and interactive executive dashboarding.

---

## 📌 Executive Summary
Analyzed **541,909 raw transactional records** (£10.28M total gross revenue) from a multinational e-commerce retailer spanning 2010 to 2011. Built a complete analytics pipeline from raw data wrangling to business strategy recommendations.

### 🎯 Key Business Questions Solved:
1. **Sales Momentum**: What is our Month-over-Month (MoM) revenue growth and seasonality pattern?
2. **Customer Retention**: At what rate do new customer cohorts churn after their initial purchase?
3. **Customer Value Distribution**: Who are our highest-value customers, and how much revenue depends on them?
4. **Churn Risk**: Which high-value customers have stopped purchasing and require urgent re-engagement?
5. **Product & Geo Pareto (80/20)**: Which products and international markets drive the majority of sales vs cancellations?

---

## 🛠️ Tech Stack & Skills Demonstrated

| Domain | Tools / Technologies | Key Concepts |
| :--- | :--- | :--- |
| **Data Cleaning & ETL** | Python 3.12, Pandas, NumPy | Anomaly detection, cancellation handling, regex, null imputation, timestamp engineering |
| **Relational Database & SQL** | SQLite3, DuckDB | CTEs, Window Functions (`LAG`, `SUM() OVER`, `ROW_NUMBER()`), Multi-table JOINs, Indexing |
| **Customer Analytics** | Python, Scipy | RFM Segmentation (Recency, Frequency, Monetary), Cohort Retention Analysis |
| **Visualization & Reporting** | Power BI, Matplotlib, Seaborn, Tailwind HTML5 | Heatmaps, dual-axis trends, Pareto distribution charts, executive dashboards |

---

## 📂 Repository Structure

```text
ecommerce-data-analytics/
├── data/
│   ├── raw/                   # Raw Online Retail dataset (541k+ transactions)
│   └── processed/             # Cleaned CSV files & indexed SQLite database
├── scripts/
│   ├── 01_clean_data.py       # Full ETL, anomaly filtering & database loading
│   ├── 02_run_sql_analytics.py# SQL execution pipeline & report exporter
│   └── 03_rfm_segmentation.py # RFM scoring, cohort heatmap & chart generation
├── sql_queries/
│   ├── 01_monthly_executive_kpis.sql      # MoM revenue growth via LAG()
│   ├── 02_cohort_retention_analysis.sql   # Month-by-month cohort matrix
│   ├── 03_product_pareto_analysis.sql     # 80/20 cumulative revenue ranking
│   └── 04_country_and_return_analysis.sql # Geographic share & return rates
├── dashboard/
│   ├── index.html             # Standalone interactive dashboard (open in any browser)
│   └── POWER_BI_TABLEAU_GUIDE.md # Star schema, DAX measures & visual blueprint
├── outputs/
│   ├── charts/                # Publication-ready charts (PNG @ 300 DPI)
│   └── reports/               # Aggregate analytical tables & audit reports
└── README.md                  # Project documentation & business insights
```

---

## 🧹 Phase 1: Data Cleaning & Wrangling Pipeline

The raw dataset presented several real-world data quality issues that required systematic auditing:
- **Missing Customer IDs**: 135,080 records (24.9%) had no CustomerID. Rather than discarding them (which would understate revenue by £1.7M), they were categorized as "Guest Checkouts" for sales tracking and filtered only for customer-level retention.
- **Cancellations & Returns**: 9,288 records started with code `'C'` and negative quantities. These were separated into a dedicated `cancellations` table to enable return rate analysis without corrupting gross sales figures.
- **Administrative Fees**: Filtered out non-merchandise SKU codes (`POST`, `D`, `BANK CHARGES`, `AMAZON FEE`).
- **Duplicates**: Removed 5,268 exact duplicate rows.

**Cleaned Output**: 522,717 validated transactions across 4,334 identified customers and 38 countries.

---

## 💡 Phase 2: Core Analytical Insights

### 1. The 80/20 Customer Concentration
- **11.47% of customers** ("Champions") account for **50.23% of total revenue**.
- Combining **Champions** and **Loyal Customers** (30.3% of total customer base) drives **72.97% of total revenue**.
- **Action**: Losing a single Champion customer is catastrophic. Implemented VIP proactive account management.

### 2. The Steep Cohort Retention Cliff
- Analysis of monthly customer cohorts reveals that customer retention drops from **100% in Month 0** to **32%–38% in Month 1**, stabilizing between **28%–36%** in subsequent months.
- **Action**: The greatest risk of churn occurs within the first 30 days. An automated re-purchase incentive delivered on Day 14 post-first-order will flatten this drop.

### 3. The "At Risk (High Value)" Win-Back Opportunity
- **450 customers** are classified as "At Risk (High Value)": they have high past purchase frequency and monetary spend, but have not made a purchase in over 90–180 days.
- They represent **£1,093,000+** in past revenue.
- **Action**: Trigger automated win-back email sequence offering a personalized restock discount.

---

## 🚀 How to Run this Project Locally

### Prerequisites
- Python 3.10+ installed
- Git

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/your-username/ecommerce-data-analytics.git
cd ecommerce-data-analytics
pip install pandas openpyxl duckdb matplotlib seaborn
```

### 2. Execute Data Pipeline
```bash
# Step 1: Clean and load data into SQLite
python scripts/01_clean_data.py

# Step 2: Run all SQL analytics queries and export reports
python scripts/02_run_sql_analytics.py

# Step 3: Compute RFM segments and generate charts
python scripts/03_rfm_segmentation.py
```

### 3. View Interactive Dashboard
Simply double click `dashboard/index.html` to open the interactive executive dashboard in your browser.
