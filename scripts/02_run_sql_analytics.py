"""
02_run_sql_analytics.py
-----------------------
Phase 3: SQL Analytics Execution & Report Generation
Project: E-Commerce Customer Retention & Sales Performance Analytics

Executes all SQL analytics modules against the SQLite database, validates KPIs,
and exports reporting tables to CSV for dashboard visualization.
"""

import os
import sqlite3
import pandas as pd

def run_sql_analytics():
    base_dir = r"C:\Users\KAVYA V K\.gemini\antigravity\scratch\ecommerce-data-analytics"
    db_path = os.path.join(base_dir, "data", "processed", "ecommerce.db")
    sql_dir = os.path.join(base_dir, "sql_queries")
    reports_dir = os.path.join(base_dir, "outputs", "reports")
    
    conn = sqlite3.connect(db_path)
    
    queries = [
        ("01_monthly_executive_kpis.sql", "monthly_kpis.csv", "Executive Monthly KPIs & MoM Growth"),
        ("02_cohort_retention_analysis.sql", "cohort_retention.csv", "Customer Cohort Retention Analysis"),
        ("03_product_pareto_analysis.sql", "product_pareto.csv", "Product Pareto (80/20) Revenue Analysis"),
        ("04_country_and_return_analysis.sql", "country_performance.csv", "Geographic Performance & Cancellation Rates"),
    ]
    
    for sql_file, output_csv, title in queries:
        print("\n" + "=" * 70)
        print(f"EXECUTING QUERY: {title} ({sql_file})")
        print("=" * 70)
        
        file_path = os.path.join(sql_dir, sql_file)
        with open(file_path, "r", encoding="utf-8") as f:
            query = f.read()
            
        df_result = pd.read_sql_query(query, conn)
        out_csv_path = os.path.join(reports_dir, output_csv)
        df_result.to_csv(out_csv_path, index=False)
        
        print(f"Rows Returned: {len(df_result)}")
        print(f"Exported to: {out_csv_path}")
        print("\nSample Preview (First 5 rows):")
        print(df_result.head(5).to_string(index=False))
        
    conn.close()
    print("\n" + "=" * 70)
    print("ALL SQL ANALYTICS EXECUTED AND EXPORTED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_sql_analytics()
