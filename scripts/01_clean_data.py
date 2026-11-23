"""
01_clean_data.py
----------------
Phase 2: Data Cleaning and Transformation Pipeline
Project: E-Commerce Customer Retention & Sales Performance Analytics

This script performs end-to-end data auditing, cleaning, feature engineering,
and loads the sanitized data into both CSV and SQLite database for SQL analytics.
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np

def run_cleaning_pipeline():
    raw_excel_path = r"C:\Users\KAVYA V K\.gemini\antigravity\scratch\ecommerce-data-analytics\data\raw\Online Retail.xlsx"
    processed_dir = r"C:\Users\KAVYA V K\.gemini\antigravity\scratch\ecommerce-data-analytics\data\processed"
    reports_dir = r"C:\Users\KAVYA V K\.gemini\antigravity\scratch\ecommerce-data-analytics\outputs\reports"
    
    print("=" * 60)
    print("STEP 1: Loading raw dataset...")
    print("=" * 60)
    df_raw = pd.read_excel(raw_excel_path)
    total_raw_rows = len(df_raw)
    print(f"Loaded {total_raw_rows:,} raw records with {len(df_raw.columns)} columns.")

    # 1. Inspect Missing Values
    null_counts = df_raw.isnull().sum()
    print("\nMissing Values Audit:")
    for col, count in null_counts.items():
        pct = (count / total_raw_rows) * 100
        print(f" - {col:15}: {count:7,} nulls ({pct:5.2f}%)")

    # 2. Duplicate Detection
    duplicate_rows = df_raw.duplicated().sum()
    print(f"\nExact Duplicate Rows Detected: {duplicate_rows:,}")

    # 3. Clean Text Columns
    df = df_raw.copy()
    df.drop_duplicates(inplace=True)
    df['Description'] = df['Description'].astype(str).str.strip()
    df['StockCode'] = df['StockCode'].astype(str).str.strip().str.upper()
    df['Country'] = df['Country'].astype(str).str.strip()

    # 4. Handle Cancellations and Quantities
    # Invoices starting with 'C' are cancellations / returns
    df['InvoiceNo_str'] = df['InvoiceNo'].astype(str).str.strip()
    df['IsCancelled'] = df['InvoiceNo_str'].str.startswith('C') | (df['Quantity'] < 0)

    # 5. Filter out non-product transactions / junk entries
    # e.g., 'POST' (Postage), 'D' (Discount), 'M' (Manual), 'BANK CHARGES', 'AMAZON FEE', etc.
    admin_codes = ['POST', 'D', 'M', 'BANK CHARGES', 'AMAZON FEE', 'CRUK', 'DOT']
    df['IsAdminCharge'] = df['StockCode'].isin(admin_codes)

    # 6. Price validation: remove negative/zero price anomalies for valid sales
    # Keep only records where UnitPrice > 0 and Quantity > 0 for completed sales
    df_completed_sales = df[
        (~df['IsCancelled']) & 
        (df['Quantity'] > 0) & 
        (df['UnitPrice'] > 0) & 
        (~df['IsAdminCharge'])
    ].copy()

    # 7. Add Derived Columns for Analytics & Financials
    df_completed_sales['InvoiceDate'] = pd.to_datetime(df_completed_sales['InvoiceDate'])
    df_completed_sales['TotalAmount'] = (df_completed_sales['Quantity'] * df_completed_sales['UnitPrice']).round(2)
    df_completed_sales['InvoiceYear'] = df_completed_sales['InvoiceDate'].dt.year
    df_completed_sales['InvoiceMonth'] = df_completed_sales['InvoiceDate'].dt.month
    df_completed_sales['YearMonth'] = df_completed_sales['InvoiceDate'].dt.to_period('M').astype(str)
    df_completed_sales['Date'] = df_completed_sales['InvoiceDate'].dt.date
    df_completed_sales['DayOfWeek'] = df_completed_sales['InvoiceDate'].dt.day_name()
    df_completed_sales['HourOfDay'] = df_completed_sales['InvoiceDate'].dt.hour

    # Customer ID formatting (fill NA with -1 to indicate Guest Checkout, or convert valid IDs to integer)
    df_completed_sales['HasCustomerID'] = df_completed_sales['CustomerID'].notnull()
    df_completed_sales['CustomerID_Clean'] = df_completed_sales['CustomerID'].fillna(-1).astype(int)

    cleaned_count = len(df_completed_sales)
    print(f"\nCleaned Completed Transactions: {cleaned_count:,} ({cleaned_count/total_raw_rows*100:.1f}% of raw)")
    print(f"Transactions with identified CustomerID: {df_completed_sales['HasCustomerID'].sum():,} ({df_completed_sales['HasCustomerID'].mean()*100:.1f}%)")
    print(f"Date Range: {df_completed_sales['InvoiceDate'].min()} to {df_completed_sales['InvoiceDate'].max()}")
    print(f"Total Revenue Generated: £{df_completed_sales['TotalAmount'].sum():,.2f}")

    # 8. Export to CSV for Power BI / Tableau
    csv_out_path = os.path.join(processed_dir, "cleaned_online_retail.csv")
    print(f"\nExporting cleaned dataset to CSV: {csv_out_path}")
    df_completed_sales.to_csv(csv_out_path, index=False)

    # 9. Export Customer-identified records (for RFM & Retention Analysis)
    df_customer_transactions = df_completed_sales[df_completed_sales['HasCustomerID']].copy()
    customer_csv_path = os.path.join(processed_dir, "customer_transactions.csv")
    df_customer_transactions.to_csv(customer_csv_path, index=False)
    print(f"Exporting customer-identified records to CSV: {customer_csv_path}")

    # 10. Load into SQLite Database for SQL Analytics
    db_path = os.path.join(processed_dir, "ecommerce.db")
    print(f"\nWriting to SQLite Database: {db_path}...")
    conn = sqlite3.connect(db_path)
    
    # Store complete cleaned transactions
    df_completed_sales.to_sql("sales", conn, if_exists="replace", index=False)
    
    # Store cancellations separately for return rate analysis!
    df_cancellations = df[df['IsCancelled']].copy()
    df_cancellations['InvoiceDate'] = pd.to_datetime(df_cancellations['InvoiceDate'])
    df_cancellations['TotalAmount'] = (df_cancellations['Quantity'] * df_cancellations['UnitPrice']).round(2)
    df_cancellations.to_sql("cancellations", conn, if_exists="replace", index=False)

    # Create Indexes for fast querying
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(InvoiceDate);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_cust ON sales(CustomerID_Clean);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_prod ON sales(StockCode);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_country ON sales(Country);")
    conn.commit()
    conn.close()
    print("Database indexing completed.")

    # 11. Write Data Cleaning Summary Report
    summary_report_path = os.path.join(reports_dir, "data_cleaning_audit.txt")
    with open(summary_report_path, "w", encoding="utf-8") as f:
        f.write("DATA CLEANING AND AUDIT REPORT\n")
        f.write("=" * 40 + "\n")
        f.write(f"Total Raw Records: {total_raw_rows:,}\n")
        f.write(f"Duplicate Records Removed: {duplicate_rows:,}\n")
        f.write(f"Total Cancelled / Refund Records: {len(df_cancellations):,}\n")
        f.write(f"Admin / Fee Records Removed: {df['IsAdminCharge'].sum():,}\n")
        f.write(f"Final Cleaned Sales Transactions: {cleaned_count:,}\n")
        f.write(f"Transactions with Customer ID: {df_completed_sales['HasCustomerID'].sum():,}\n")
        f.write(f"Total Gross Revenue: £{df_completed_sales['TotalAmount'].sum():,.2f}\n")
        f.write(f"Unique Customers (Identified): {df_completed_sales.loc[df_completed_sales['HasCustomerID'], 'CustomerID_Clean'].nunique():,}\n")
        f.write(f"Unique Products Sold: {df_completed_sales['StockCode'].nunique():,}\n")
        f.write(f"Unique Countries Served: {df_completed_sales['Country'].nunique():,}\n")
        f.write(f"Date Span: {df_completed_sales['InvoiceDate'].min()} to {df_completed_sales['InvoiceDate'].max()}\n")
    print(f"Summary report generated at: {summary_report_path}")
    print("\nData cleaning pipeline finished successfully!")

if __name__ == "__main__":
    run_cleaning_pipeline()
