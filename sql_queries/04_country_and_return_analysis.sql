-- ============================================================
-- 04_country_and_return_analysis.sql
-- Goal: Geographic Performance and Return/Cancellation Rates
-- Concepts: LEFT JOIN between Sales and Cancellations, CASE WHEN, GROUP BY
-- ============================================================

WITH country_sales AS (
    SELECT 
        Country,
        COUNT(DISTINCT InvoiceNo) AS CompletedOrders,
        COUNT(DISTINCT CASE WHEN CustomerID_Clean != -1 THEN CustomerID_Clean END) AS UniqueCustomers,
        ROUND(SUM(TotalAmount), 2) AS TotalGrossRevenue,
        ROUND(SUM(TotalAmount) / COUNT(DISTINCT InvoiceNo), 2) AS CountryAOV
    FROM sales
    GROUP BY Country
),
country_cancellations AS (
    SELECT 
        Country,
        COUNT(DISTINCT InvoiceNo) AS CancelledOrders,
        ABS(ROUND(SUM(TotalAmount), 2)) AS CancelledRevenueValue
    FROM cancellations
    GROUP BY Country
)
SELECT 
    s.Country,
    s.CompletedOrders,
    COALESCE(c.CancelledOrders, 0) AS CancelledOrders,
    (s.CompletedOrders + COALESCE(c.CancelledOrders, 0)) AS TotalOrderAttempts,
    ROUND(
        (CAST(COALESCE(c.CancelledOrders, 0) AS FLOAT) / 
        (s.CompletedOrders + COALESCE(c.CancelledOrders, 0))) * 100, 
        2
    ) AS CancellationRate_Pct,
    s.TotalGrossRevenue,
    s.CountryAOV,
    ROUND((s.TotalGrossRevenue / (SELECT SUM(TotalAmount) FROM sales)) * 100, 2) AS GlobalRevenueShare_Pct
FROM country_sales s
LEFT JOIN country_cancellations c ON s.Country = c.Country
ORDER BY s.TotalGrossRevenue DESC;
