-- DecisionIQ Enterprise Operational Intelligence
-- Advanced SQL Analytical Queries
-- Compatible with PostgreSQL and SQLite (standard ANSI SQL)

-- ========================================================
-- 1. TIME INTELLIGENCE & REVENUE GROWTH (MoM & YoY)
-- ========================================================
-- Purpose: Track monthly sales revenue, rolling 3-month average, and Month-over-Month growth.
-- Solves: Financial reporting visibility and identifying growth inflections.

WITH MonthlyRevenue AS (
    SELECT 
        STRFTIME('%Y-%m', order_date) AS order_month, -- SQLite syntax (Postgres would use TO_CHAR(order_date, 'YYYY-MM'))
        SUM(total_amount) AS revenue,
        COUNT(order_id) AS order_count
    FROM orders
    WHERE status NOT IN ('Cancelled', 'Refunded')
    GROUP BY 1
),
RollingMetrics AS (
    SELECT 
        order_month,
        revenue,
        order_count,
        LAG(revenue, 1) OVER (ORDER BY order_month) AS prev_month_revenue,
        LAG(revenue, 12) OVER (ORDER BY order_month) AS prev_year_revenue,
        AVG(revenue) OVER (ORDER BY order_month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3mo_avg_revenue
    FROM MonthlyRevenue
)
SELECT 
    order_month,
    revenue,
    order_count,
    prev_month_revenue,
    ROUND(((revenue - prev_month_revenue) / prev_month_revenue) * 100.0, 2) AS mom_growth_pct,
    prev_year_revenue,
    ROUND(((revenue - prev_year_revenue) / prev_year_revenue) * 100.0, 2) AS yoy_growth_pct,
    ROUND(rolling_3mo_avg_revenue, 2) AS rolling_3mo_avg_revenue
FROM RollingMetrics
ORDER BY order_month DESC;


-- ========================================================
-- 2. CUSTOMER COHORT RETENTION ANALYSIS (12-MONTH HORIZON)
-- ========================================================
-- Purpose: Track monthly acquisition cohorts and their repeat purchasing behavior.
-- Solves: Measuring customer loyalty, LTV trajectory, and product-market fit.

WITH CustomerCohorts AS (
    -- Get acquisition month for each customer
    SELECT 
        customer_id,
        STRFTIME('%Y-%m', acquisition_date) AS cohort_month
    FROM customers
),
CustomerActivity AS (
    -- Find all distinct months when a customer made a purchase
    SELECT DISTINCT
        o.customer_id,
        STRFTIME('%Y-%m', o.order_date) AS activity_month
    FROM orders o
    WHERE o.status NOT IN ('Cancelled')
),
CohortSizes AS (
    -- Count total customers in each cohort
    SELECT 
        cohort_month,
        COUNT(customer_id) AS cohort_size
    FROM CustomerCohorts
    GROUP BY 1
),
CohortRetention AS (
    -- Calculate month index difference (Retention Month 0, 1, 2... 12)
    SELECT 
        cc.cohort_month,
        ca.activity_month,
        -- Calculate difference in months between cohort month and activity month
        ((CAST(SUBSTR(ca.activity_month, 1, 4) AS INTEGER) - CAST(SUBSTR(cc.cohort_month, 1, 4) AS INTEGER)) * 12) +
        (CAST(SUBSTR(ca.activity_month, 6, 2) AS INTEGER) - CAST(SUBSTR(cc.cohort_month, 6, 2) AS INTEGER)) AS month_number,
        COUNT(DISTINCT cc.customer_id) AS active_customers
    FROM CustomerCohorts cc
    JOIN CustomerActivity ca ON cc.customer_id = ca.customer_id
    WHERE month_number >= 0 AND month_number <= 12
    GROUP BY 1, 2, 3
)
SELECT 
    cr.cohort_month,
    cs.cohort_size,
    cr.month_number,
    cr.active_customers,
    ROUND((cr.active_customers * 100.0) / cs.cohort_size, 2) AS retention_pct
FROM CohortRetention cr
JOIN CohortSizes cs ON cr.cohort_month = cs.cohort_month
ORDER BY cr.cohort_month DESC, cr.month_number ASC;


-- ========================================================
-- 3. RFM CUSTOMER SEGMENTATION
-- ========================================================
-- Purpose: Segment customers based on Recency (R), Frequency (F), and Monetary Value (M).
-- Solves: Targeted marketing campaign design and proactive Customer Success planning.

WITH CustomerMetrics AS (
    SELECT 
        customer_id,
        -- Recency: Days since last order relative to the data warehouse's latest order date
        (SELECT JULIANDAY(MAX(order_date)) FROM orders) - JULIANDAY(MAX(order_date)) AS recency_days,
        -- Frequency: Total orders placed
        COUNT(order_id) AS frequency,
        -- Monetary Value: Total spending on successful orders
        SUM(total_amount) AS monetary_value
    FROM orders
    WHERE status NOT IN ('Cancelled')
    GROUP BY customer_id
),
RFMRanks AS (
    -- Divide customers into quintiles (1-5) for each RFM parameter
    -- Note: Lower recency_days is better, so we rank order DESC to make 5 represent the most recent purchasers
    SELECT 
        customer_id,
        recency_days,
        frequency,
        monetary_value,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM CustomerMetrics
),
RFMSegments AS (
    SELECT 
        c.customer_id,
        c.company_name,
        r.recency_days,
        r.frequency,
        r.monetary_value,
        r.r_score,
        r.f_score,
        r.m_score,
        (r.r_score + r.f_score + r.m_score) AS total_rfm_score
    FROM RFMRanks r
    JOIN customers c ON r.customer_id = c.customer_id
)
SELECT 
    customer_id,
    company_name,
    recency_days,
    frequency,
    monetary_value,
    r_score,
    f_score,
    m_score,
    total_rfm_score,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Buyers'
        WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At-Risk Customers'
        WHEN r_score <= 1 THEN 'Lost Customers'
        ELSE 'Needs Attention / Promising'
    END AS customer_segment_tag
FROM RFMSegments
ORDER BY total_rfm_score DESC, monetary_value DESC
LIMIT 50;


-- ========================================================
-- 4. INVENTORY AGING & STOCKOUT RISK DIAGNOSTICS
-- ========================================================
-- Purpose: Diagnose inventory speed and identify items at risk of running out.
-- Solves: Optimizing working capital and preventing sales disruption.

WITH ProductDailySales AS (
    -- Calculate moving 30-day average daily sales volume for physical products
    SELECT 
        od.product_id,
        SUM(od.quantity) / 90.0 AS avg_daily_sales_90d
    FROM order_details od
    JOIN orders o ON od.order_id = o.order_id
    WHERE o.order_date >= (SELECT DATE(MAX(order_date), '-90 days') FROM orders)
      AND o.status NOT IN ('Cancelled')
    GROUP BY od.product_id
)
SELECT 
    w.warehouse_name,
    p.product_name,
    p.sku,
    p.category,
    i.quantity_on_hand,
    i.reorder_point,
    ROUND(COALESCE(s.avg_daily_sales_90d, 0.0), 2) AS avg_daily_sales_90d,
    CASE 
        WHEN COALESCE(s.avg_daily_sales_90d, 0.0) = 0 THEN 999
        ELSE ROUND(i.quantity_on_hand / s.avg_daily_sales_90d, 1)
    END AS days_inventory_on_hand,
    CASE 
        WHEN i.quantity_on_hand <= i.reorder_point THEN 'CRITICAL: Reorder Triggered'
        WHEN i.quantity_on_hand < (COALESCE(s.avg_daily_sales_90d, 0.0) * 15) THEN 'HIGH RISK: Stockout Warning (<15d)'
        WHEN i.quantity_on_hand > (COALESCE(s.avg_daily_sales_90d, 0.0) * 90) THEN 'WARNING: Slow Moving (>90d)'
        ELSE 'Healthy / Optimal'
    END AS stock_health_status
FROM inventory i
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
JOIN products p ON i.product_id = p.product_id
LEFT JOIN ProductDailySales s ON i.product_id = s.product_id
ORDER BY days_inventory_on_hand ASC;


-- ========================================================
-- 5. REVENUE LEAKAGE ANALYSIS (RECONCILIATION)
-- ========================================================
-- Purpose: Calculate leaking revenue segments (cancellations, refunds, payment failures).
-- Solves: Gross-to-Net revenue reconciliation, pointing to support and credit issues.

SELECT 
    STRFTIME('%Y-%m', o.order_date) AS order_month,
    SUM(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE 0 END) AS net_completed_revenue,
    SUM(CASE WHEN o.status = 'Refunded' THEN o.total_amount ELSE 0 END) AS leaked_refund_revenue,
    SUM(CASE WHEN o.status = 'Cancelled' THEN o.total_amount ELSE 0 END) AS leaked_cancelled_revenue,
    -- Add failed payments leakage
    SUM(CASE WHEN p.payment_status = 'Failed' THEN o.total_amount ELSE 0 END) AS leaked_failed_payment_revenue,
    -- Calculate gross revenue before leakage
    SUM(o.total_amount) AS gross_potential_revenue,
    -- Calculate leakage rate
    ROUND(
        (SUM(CASE WHEN o.status IN ('Refunded', 'Cancelled') OR p.payment_status = 'Failed' THEN o.total_amount ELSE 0 END) * 100.0) /
        SUM(o.total_amount), 2
    ) AS revenue_leakage_pct
FROM orders o
LEFT JOIN payments p ON o.order_id = p.order_id
GROUP BY 1
ORDER BY 1 DESC;


-- ========================================================
-- 6. LOGISTICS & SUPPLIER RELIABILITY SCORECARD
-- ========================================================
-- Purpose: Score suppliers and warehouse logistics bottlenecks.
-- Solves: Supply chain risk management and vendor negotiation.

SELECT 
    s.supplier_name,
    w.warehouse_name,
    COUNT(shp.shipment_id) AS total_shipments,
    ROUND(AVG(JULIANDAY(shp.actual_delivery_date) - JULIANDAY(shp.shipment_date)), 1) AS avg_transit_days,
    ROUND(AVG(JULIANDAY(shp.actual_delivery_date) - JULIANDAY(shp.estimated_delivery_date)), 1) AS avg_delay_days,
    SUM(CASE WHEN shp.delivery_status = 'Late' THEN 1 ELSE 0 END) AS late_shipment_count,
    ROUND(
        (SUM(CASE WHEN shp.delivery_status = 'Late' THEN 1 ELSE 0 END) * 100.0) / COUNT(shp.shipment_id), 2
    ) AS late_shipment_rate_pct,
    ROUND(AVG(s.reliability_score), 2) AS contract_supplier_reliability
FROM shipments shp
JOIN suppliers s ON shp.supplier_id = s.supplier_id
JOIN warehouses w ON shp.warehouse_id = w.warehouse_id
WHERE shp.actual_delivery_date IS NOT NULL
GROUP BY 1, 2
ORDER BY late_shipment_rate_pct DESC;


-- ========================================================
-- 7. RECURSIVE CTE: EMPLOYEE ORGANIZATIONAL HIERARCHY & REVENUE ROLLS
-- ========================================================
-- Purpose: Map manager-subordinate lines and compile roll-up revenue managed.
-- Solves: Departmental restructuring and organizational performance audits.

WITH RECURSIVE OrgHierarchy AS (
    -- Anchor member: CEO (Arthurs reports_to is null)
    SELECT 
        employee_id,
        first_name || ' ' || last_name AS employee_name,
        role,
        department,
        reports_to,
        1 AS level_depth,
        first_name || ' ' || last_name AS path_name
    FROM employees
    WHERE reports_to IS NULL
    
    UNION ALL
    
    -- Recursive member: Find subordinates and build path
    SELECT 
        e.employee_id,
        e.first_name || ' ' || e.last_name AS employee_name,
        e.role,
        e.department,
        e.reports_to,
        h.level_depth + 1 AS level_depth,
        h.path_name || ' -> ' || e.first_name || ' ' || e.last_name AS path_name
    FROM employees e
    JOIN OrgHierarchy h ON e.reports_to = h.employee_id
),
SalesRevenue AS (
    -- Sum up direct revenue managed by each sales rep
    SELECT 
        sales_representative_id AS employee_id,
        SUM(total_amount) AS direct_sales_revenue
    FROM orders
    WHERE status NOT IN ('Cancelled')
    GROUP BY 1
)
SELECT 
    oh.level_depth,
    oh.employee_name,
    oh.role,
    oh.department,
    oh.path_name,
    COALESCE(sr.direct_sales_revenue, 0.0) AS direct_revenue_generated
FROM OrgHierarchy oh
LEFT JOIN SalesRevenue sr ON oh.employee_id = sr.employee_id
ORDER BY oh.level_depth, oh.department;
