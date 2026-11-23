-- ============================================================
-- 02_cohort_retention_analysis.sql
-- Goal: Measure Customer Retention by Acquisition Cohort
-- Concepts: CTEs, Window Functions (MIN OVER PARTITION), Cohort Indexing
-- ============================================================

WITH customer_first_purchase AS (
    SELECT 
        CustomerID_Clean AS CustomerID,
        MIN(InvoiceDate) AS FirstPurchaseDate,
        strftime('%Y-%m', MIN(InvoiceDate)) AS FirstPurchaseMonth
    FROM sales
    WHERE CustomerID_Clean != -1
    GROUP BY CustomerID_Clean
),
cohort_transactions AS (
    SELECT 
        s.CustomerID_Clean AS CustomerID,
        c.FirstPurchaseMonth,
        strftime('%Y-%m', s.InvoiceDate) AS TransactionMonth,
        (CAST(strftime('%Y', s.InvoiceDate) AS INT) - CAST(strftime('%Y', c.FirstPurchaseDate) AS INT)) * 12 +
        (CAST(strftime('%m', s.InvoiceDate) AS INT) - CAST(strftime('%m', c.FirstPurchaseDate) AS INT)) AS CohortPeriod
    FROM sales s
    JOIN customer_first_purchase c ON s.CustomerID_Clean = c.CustomerID
),
cohort_summary AS (
    SELECT 
        FirstPurchaseMonth,
        CohortPeriod,
        COUNT(DISTINCT CustomerID) AS ActiveCustomers
    FROM cohort_transactions
    GROUP BY FirstPurchaseMonth, CohortPeriod
),
cohort_base AS (
    SELECT 
        FirstPurchaseMonth,
        ActiveCustomers AS CohortOriginalSize
    FROM cohort_summary
    WHERE CohortPeriod = 0
)
SELECT 
    cs.FirstPurchaseMonth,
    cb.CohortOriginalSize,
    cs.CohortPeriod,
    cs.ActiveCustomers,
    ROUND((CAST(cs.ActiveCustomers AS FLOAT) / cb.CohortOriginalSize) * 100, 2) AS RetentionRate_Pct
FROM cohort_summary cs
JOIN cohort_base cb ON cs.FirstPurchaseMonth = cb.FirstPurchaseMonth
ORDER BY cs.FirstPurchaseMonth, cs.CohortPeriod;
