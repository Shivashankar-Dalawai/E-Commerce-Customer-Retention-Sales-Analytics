"""
03_rfm_segmentation.py
-----------------------
Phase 4: Customer RFM Segmentation & Visual Analytics
Project: E-Commerce Customer Retention & Sales Performance Analytics

Computes Recency, Frequency, and Monetary (RFM) metrics for every identified customer,
segments them into actionable behavioral personas, and generates publication-ready visualizations.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set style for publication-ready visual charts
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.size'] = 11

def run_rfm_analysis():
    base_dir = r"C:\Users\KAVYA V K\.gemini\antigravity\scratch\ecommerce-data-analytics"
    customer_csv = os.path.join(base_dir, "data", "processed", "customer_transactions.csv")
    charts_dir = os.path.join(base_dir, "outputs", "charts")
    reports_dir = os.path.join(base_dir, "outputs", "reports")
    
    print("=" * 60)
    print("STEP 1: Loading customer transaction data...")
    print("=" * 60)
    df = pd.read_csv(customer_csv)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # 1. Snapshot Date: 1 day after the latest transaction
    snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    print(f"Dataset Latest Date: {df['InvoiceDate'].max().date()} | Snapshot Date: {snapshot_date.date()}")
    
    # 2. Calculate RFM Metrics per Customer
    rfm = df.groupby('CustomerID_Clean').agg(
        Recency=('InvoiceDate', lambda x: (snapshot_date - x.max()).days),
        Frequency=('InvoiceNo', 'nunique'),
        Monetary=('TotalAmount', 'sum'),
        FirstPurchase=('InvoiceDate', 'min'),
        LastPurchase=('InvoiceDate', 'max')
    ).reset_index()
    
    rfm.rename(columns={'CustomerID_Clean': 'CustomerID'}, inplace=True)
    rfm['Monetary'] = rfm['Monetary'].round(2)
    
    print(f"Total Unique Identified Customers: {len(rfm):,}")
    print(f"Median Recency: {rfm['Recency'].median()} days")
    print(f"Median Frequency: {rfm['Frequency'].median()} orders")
    print(f"Median Monetary Spend: £{rfm['Monetary'].median():,.2f}")
    
    # 3. Score R, F, M into Quartiles (1 to 4)
    # Recency: Lower is better (1 = highest recency/cold, 4 = lowest recency/recent)
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1]).astype(int)
    
    # Frequency: Higher is better (Rank-based handling for ties)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4]).astype(int)
    
    # Monetary: Higher is better
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4]).astype(int)
    
    # Combined RFM Score
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    rfm['RFM_Index'] = rfm[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)

    # 4. Map Behavioral Customer Segments
    def assign_segment(row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 3 and f <= 2 and m >= 2:
            return 'Potential Loyalists'
        elif r >= 4 and f == 1:
            return 'Recent New Customers'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At Risk (High Value)'
        elif r <= 2 and f >= 2:
            return 'Customers Needing Attention'
        elif r == 1 and f == 1:
            return 'Lost / Hibernating'
        else:
            return 'Promising Regulars'
            
    rfm['Customer_Segment'] = rfm.apply(assign_segment, axis=1)
    
    # Export RFM customer database
    rfm_csv_path = os.path.join(reports_dir, "rfm_customer_segments.csv")
    rfm.to_csv(rfm_csv_path, index=False)
    print(f"\nRFM Customer Segments saved to: {rfm_csv_path}")

    # 5. Segment Summary Metrics
    segment_summary = rfm.groupby('Customer_Segment').agg(
        Customer_Count=('CustomerID', 'count'),
        Avg_Recency_Days=('Recency', 'mean'),
        Avg_Frequency_Orders=('Frequency', 'mean'),
        Total_Revenue=('Monetary', 'sum'),
        Avg_Revenue_Per_Cust=('Monetary', 'mean')
    ).round(2).reset_index()
    
    total_cust = len(rfm)
    total_rev = rfm['Monetary'].sum()
    segment_summary['Customer_Share_Pct'] = (segment_summary['Customer_Count'] / total_cust * 100).round(2)
    segment_summary['Revenue_Share_Pct'] = (segment_summary['Total_Revenue'] / total_rev * 100).round(2)
    segment_summary = segment_summary.sort_values(by='Total_Revenue', ascending=False)
    
    segment_summary_path = os.path.join(reports_dir, "segment_summary.csv")
    segment_summary.to_csv(segment_summary_path, index=False)
    print(f"Segment Summary saved to: {segment_summary_path}")
    print("\nCustomer Segment Breakdown:")
    print(segment_summary[['Customer_Segment', 'Customer_Count', 'Customer_Share_Pct', 'Revenue_Share_Pct']].to_string(index=False))

    # ==========================================================
    # CHART GENERATION
    # ==========================================================
    print("\n" + "=" * 60)
    print("STEP 2: Generating Portfolio Visualizations...")
    print("=" * 60)
    
    # CHART 1: Customer Segment vs Revenue Share Bar Chart
    plt.figure(figsize=(11, 6))
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
    bars = plt.barh(segment_summary['Customer_Segment'], segment_summary['Revenue_Share_Pct'], color='#2563EB', alpha=0.85)
    plt.title('Revenue Contribution by Customer Segment (%)', fontsize=14, weight='bold', pad=15)
    plt.xlabel('Share of Total Revenue (%)', fontsize=12)
    plt.gca().invert_yaxis()
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.1f}%", va='center', fontsize=10, weight='bold')
    plt.tight_layout()
    chart1_path = os.path.join(charts_dir, "01_revenue_by_segment.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Chart 1 saved: {chart1_path}")

    # CHART 2: Monthly Revenue & MoM Growth Dual-Axis Chart
    monthly_csv = os.path.join(reports_dir, "monthly_kpis.csv")
    df_monthly = pd.read_csv(monthly_csv)
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    
    # Bar chart for revenue in thousands
    bars = ax1.bar(df_monthly['YearMonth'], df_monthly['TotalRevenue'] / 1000, color='#3B82F6', alpha=0.7, label='Monthly Revenue (£k)')
    # Line chart for MoM growth
    line = ax2.plot(df_monthly['YearMonth'], df_monthly['MoM_Revenue_Growth_Pct'], color='#DC2626', marker='o', linewidth=2.5, label='MoM Growth %')
    ax2.axhline(0, color='gray', linestyle='--', alpha=0.6)
    
    ax1.set_xlabel('Month', fontsize=12, labelpad=10)
    ax1.set_ylabel('Revenue (£ Thousands)', fontsize=12, color='#1E40AF')
    ax2.set_ylabel('Month-over-Month Growth (%)', fontsize=12, color='#DC2626')
    ax1.tick_params(axis='x', rotation=45)
    plt.title('Monthly Sales Revenue & MoM Growth Trajectory (2010 - 2011)', fontsize=14, weight='bold', pad=15)
    fig.tight_layout()
    chart2_path = os.path.join(charts_dir, "02_monthly_sales_growth.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Chart 2 saved: {chart2_path}")

    # CHART 3: Cohort Retention Heatmap
    cohort_csv = os.path.join(reports_dir, "cohort_retention.csv")
    df_cohort = pd.read_csv(cohort_csv)
    cohort_pivot = df_cohort.pivot(index='FirstPurchaseMonth', columns='CohortPeriod', values='RetentionRate_Pct')
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(
        cohort_pivot, 
        annot=True, 
        fmt=".1f", 
        cmap='YlGnBu', 
        vmin=0, 
        vmax=50, 
        cbar_kws={'label': 'Retention Rate (%)'},
        linewidths=0.5
    )
    plt.title('Customer Retention Heatmap by Acquisition Cohort', fontsize=15, weight='bold', pad=15)
    plt.xlabel('Cohort Period (Months Since First Purchase)', fontsize=12)
    plt.ylabel('Cohort Acquisition Month', fontsize=12)
    plt.tight_layout()
    chart3_path = os.path.join(charts_dir, "03_cohort_retention_heatmap.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"Chart 3 saved: {chart3_path}")

    # CHART 4: RFM Recency vs Frequency with Monetary Size
    plt.figure(figsize=(10, 6))
    sample_rfm = rfm.sample(n=min(1500, len(rfm)), random_state=42)
    scatter = plt.scatter(
        sample_rfm['Recency'], 
        sample_rfm['Frequency'], 
        c=np.log1p(sample_rfm['Monetary']), 
        cmap='viridis', 
        alpha=0.6, 
        edgecolors='none', 
        s=40
    )
    cbar = plt.colorbar(scatter)
    cbar.set_label('Log(Total Spend £)', fontsize=11)
    plt.title('RFM Distribution: Purchase Recency vs Order Frequency', fontsize=14, weight='bold', pad=15)
    plt.xlabel('Recency (Days Since Last Purchase)', fontsize=12)
    plt.ylabel('Order Frequency (Total Distinct Invoices)', fontsize=12)
    plt.ylim(0, sample_rfm['Frequency'].quantile(0.99) + 5)
    plt.tight_layout()
    chart4_path = os.path.join(charts_dir, "04_rfm_recency_frequency.png")
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    print(f"Chart 4 saved: {chart4_path}")

    print("\nAll 4 publication-quality charts generated successfully!")

if __name__ == "__main__":
    run_rfm_analysis()
