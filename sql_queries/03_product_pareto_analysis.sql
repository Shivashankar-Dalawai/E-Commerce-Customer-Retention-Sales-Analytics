-- ============================================================
-- 03_product_pareto_analysis.sql
-- Goal: Identify Top Products and evaluate the 80/20 Pareto Principle
-- Concepts: Window Functions (SUM OVER), Cumulative Totals, Percentiles
-- ============================================================

WITH product_revenue AS (
    SELECT 
        StockCode,
        MAX(Description) AS Description,
        COUNT(DISTINCT InvoiceNo) AS OrderOccurrences,
        SUM(Quantity) AS TotalUnitsSold,
        ROUND(SUM(TotalAmount), 2) AS ProductRevenue
    FROM sales
    GROUP BY StockCode
    HAVING ProductRevenue > 0
),
ranked_products AS (
    SELECT 
        StockCode,
        Description,
        OrderOccurrences,
        TotalUnitsSold,
        ProductRevenue,
        ROW_NUMBER() OVER (ORDER BY ProductRevenue DESC) AS RevenueRank,
        COUNT(*) OVER () AS TotalDistinctProducts,
        SUM(ProductRevenue) OVER (ORDER BY ProductRevenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS CumulativeRevenue,
        SUM(ProductRevenue) OVER () AS TotalStoreRevenue
    FROM product_revenue
)
SELECT 
    RevenueRank,
    StockCode,
    Description,
    OrderOccurrences,
    TotalUnitsSold,
    ProductRevenue,
    ROUND((CAST(RevenueRank AS FLOAT) / TotalDistinctProducts) * 100, 2) AS Product_Percentile,
    ROUND((CumulativeRevenue / TotalStoreRevenue) * 100, 2) AS Cumulative_Revenue_Pct,
    CASE 
        WHEN (CumulativeRevenue / TotalStoreRevenue) <= 0.80 THEN 'Top 80% Core Revenue Driver'
        ELSE 'Long Tail Product'
    END AS Pareto_Classification
FROM ranked_products
ORDER BY RevenueRank
LIMIT 50;
