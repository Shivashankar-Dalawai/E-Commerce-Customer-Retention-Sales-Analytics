# Power BI & Tableau Implementation Guide
**Project: E-Commerce Customer Retention & Sales Performance Analytics**

This guide provides the exact specifications, data modeling schema, DAX formulas, and visual layouts to recreate an enterprise-grade BI dashboard in Power BI or Tableau.

---

## 1. Data Model Architecture (Star Schema)

Import the processed datasets located in `data/processed/` and `outputs/reports/`:
1. **Fact Table (`Fact_Sales`)**: `cleaned_online_retail.csv`
2. **Dimension Table (`Dim_Customer`)**: `rfm_customer_segments.csv` (Key: `CustomerID` -> `CustomerID_Clean`)
3. **Dimension Table (`Dim_Calendar`)**: Generated Date Table (1-to-many relationship with `InvoiceDate`)

```
   ┌────────────────────────┐
   │      Dim_Calendar      │
   └───────────┬────────────┘
               │ 1
               │
               │ *
   ┌───────────┴────────────┐             ┌────────────────────────┐
   │       Fact_Sales       │ *         1 │      Dim_Customer      │
   │   (Transactions Fact)  ├─────────────┤    (RFM Segments)      │
   └────────────────────────┘ CustomerID  └────────────────────────┘
```

---

## 2. Production DAX Measures (Power BI)

Create a dedicated measure table called `_KeyMeasures` and insert the following formulas:

### Basic Financial & Volume KPIs
```dax
Total Revenue = SUM(Fact_Sales[TotalAmount])

Total Orders = DISTINCTCOUNT(Fact_Sales[InvoiceNo])

Total Units Sold = SUM(Fact_Sales[Quantity])

Average Order Value (AOV) = DIVIDE([Total Revenue], [Total Orders], 0)

Active Identified Customers = 
CALCULATE(
    DISTINCTCOUNT(Fact_Sales[CustomerID_Clean]),
    Fact_Sales[CustomerID_Clean] <> -1
)
```

### Time-Intelligence & MoM Growth
```dax
Prior Month Revenue = 
CALCULATE(
    [Total Revenue],
    DATEADD('Dim_Calendar'[Date], -1, MONTH)
)

MoM Revenue Growth % = 
DIVIDE(
    [Total Revenue] - [Prior Month Revenue],
    [Prior Month Revenue],
    0
)
```

### Customer Value & Segment KPIs
```dax
Revenue per Active Customer = 
DIVIDE([Total Revenue], [Active Identified Customers], 0)

Champion Revenue Contribution % = 
DIVIDE(
    CALCULATE([Total Revenue], Dim_Customer[Customer_Segment] = "Champions"),
    [Total Revenue],
    0
)
```

---

## 3. Recommended 3-Page Dashboard Layout

### Page 1: Executive KPI Overview & Revenue Trends
- **Top Metric Cards**: Total Revenue (£10.28M), Total Orders (22.2k), AOV (£463), Active Customers (4,334).
- **Primary Visual**: Monthly Revenue trend bar chart with dual-axis MoM Growth % line.
- **Secondary Visual**: Global Map / Top 5 Countries by Revenue Share (UK 85.1%, Netherlands 2.8%, EIRE 2.7%, Germany 2.0%, France 1.8%).
- **Slicers**: Date Range Picker, Country Dropdown.

### Page 2: Customer Retention & RFM Behavioral Segmentation
- **Key Insight Card**: "Top 11.5% of customers (Champions) account for 50.2% of total revenue".
- **Primary Visual**: Treemap / Horizontal Bar Chart of Revenue Share by `Customer_Segment`.
- **Secondary Visual**: Cohort Retention Matrix Heatmap showing retention decline across Months 0 to 12.
- **Actionable Table**: Filterable list of "At Risk (High Value)" customers displaying Last Purchase Date, Recency Days, and Lifetime Spend for CRM win-back emails.

### Page 3: Product Performance & Pareto 80/20 Distribution
- **Pareto Line Chart**: Cumulative Product Revenue % vs Product Rank (demonstrating that the top ~20% of catalog items generate 80% of revenue).
- **Top 10 Products Table**: StockCode, Description, Total Units Sold, Revenue, Return/Cancellation Count.
- **Slicers**: Product Category, Sales Volume Tier.
