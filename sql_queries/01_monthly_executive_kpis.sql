-- ============================================================
-- 01_monthly_executive_kpis.sql
-- Goal: Calculate Monthly Sales, Orders, AOV, and MoM Growth %
-- Concepts: Aggregate Functions, Window Functions (LAG), Date Parsing
-- ============================================================

WITH monthly_metrics AS (
    SELECT 
        YearMonth,
        COUNT(DISTINCT InvoiceNo) AS TotalOrders,
        COUNT(DISTINCT CASE WHEN CustomerID_Clean != -1 THEN CustomerID_Clean END) AS ActiveIdentifiedCustomers,
        SUM(Quantity) AS TotalUnitsSold,
        ROUND(SUM(TotalAmount), 2) AS TotalRevenue,
        ROUND(SUM(TotalAmount) / COUNT(DISTINCT InvoiceNo), 2) AS AverageOrderValue
    FROM sales
    GROUP BY YearMonth
),
growth_calculation AS (
    SELECT 
        YearMonth,
        TotalOrders,
        ActiveIdentifiedCustomers,
        TotalUnitsSold,
        TotalRevenue,
        AverageOrderValue,
        LAG(TotalRevenue, 1) OVER (ORDER BY YearMonth) AS PrevMonthRevenue,
        ROUND(
            ((TotalRevenue - LAG(TotalRevenue, 1) OVER (ORDER BY YearMonth)) / 
             LAG(TotalRevenue, 1) OVER (ORDER BY YearMonth)) * 100, 
            2
        ) AS MoM_Revenue_Growth_Pct
    FROM monthly_metrics
)
SELECT * 
FROM growth_calculation
ORDER BY YearMonth;
