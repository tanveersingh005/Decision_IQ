import pandas as pd
from sqlalchemy import text
from etl.db_connector import get_engine

def get_executive_kpis():
    """
    Computes top-level C-Suite KPIs from the database.
    """
    engine = get_engine()
    kpis = {}
    
    with engine.connect() as conn:
        # Total Sales & Orders (Successful only)
        sales_query = text("""
            SELECT 
                SUM(total_amount) AS total_revenue,
                COUNT(order_id) AS total_orders,
                AVG(total_amount) AS avg_order_value
            FROM orders 
            WHERE status NOT IN ('Cancelled', 'Refunded')
        """)
        res = conn.execute(sales_query).fetchone()
        kpis["total_revenue"] = float(res[0]) if res[0] else 0.0
        kpis["total_orders"] = int(res[1]) if res[1] else 0
        kpis["avg_order_value"] = float(res[2]) if res[2] else 0.0
        
        # Gross margin
        margin_query = text("""
            SELECT 
                SUM(od.subtotal) AS gross_sales,
                SUM(od.quantity * p.unit_cost) AS total_cost
            FROM order_details od
            JOIN products p ON od.product_id = p.product_id
            JOIN orders o ON od.order_id = o.order_id
            WHERE o.status NOT IN ('Cancelled', 'Refunded')
        """)
        res = conn.execute(margin_query).fetchone()
        gross = float(res[0]) if res[0] else 0.0
        cost = float(res[1]) if res[1] else 0.0
        margin = gross - cost
        kpis["margin"] = margin
        kpis["margin_pct"] = (margin / gross * 100) if gross > 0 else 0.0
        
        # Customer Support CSAT
        csat_query = text("""
            SELECT AVG(satisfaction_score) 
            FROM customer_support 
            WHERE satisfaction_score IS NOT NULL
        """)
        res = conn.execute(csat_query).fetchone()
        kpis["csat"] = float(res[0]) if res[0] else 0.0
        
        # Active Customers
        cust_query = text("SELECT COUNT(*) FROM customers WHERE status = 'Active'")
        res = conn.execute(cust_query).fetchone()
        kpis["active_customers"] = int(res[0]) if res[0] else 0
        
        # Churn Rate
        churn_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM customers WHERE status = 'Churned') * 100.0 / 
                COUNT(*) AS churn_rate
            FROM customers
        """)
        res = conn.execute(churn_query).fetchone()
        kpis["churn_rate"] = float(res[0]) if res[0] else 0.0
        
        # Calculate Business Health Score (Weighted average of metrics, max 100)
        # Revenue target = $20M, CSAT target = 5.0, Churn target = 0%
        # Standard calculation:
        csat_factor = (kpis["csat"] / 5.0) * 30  # 30 pts
        margin_factor = (kpis["margin_pct"] / 100.0) * 30 # 30 pts
        churn_factor = max(0, 20 - (kpis["churn_rate"] * 2)) # 20 pts
        active_factor = min(20, (kpis["active_customers"] / 500.0) * 20) # 20 pts
        
        kpis["health_score"] = min(100.0, csat_factor + margin_factor + churn_factor + active_factor)
        
    return kpis

def get_regional_performance():
    """
    Returns revenue and metrics grouped by region.
    """
    engine = get_engine()
    query = """
        SELECT 
            r.region_name,
            r.manager_name,
            SUM(CASE WHEN o.status NOT IN ('Cancelled', 'Refunded') THEN o.total_amount ELSE 0 END) AS net_revenue,
            COUNT(o.order_id) AS total_orders,
            SUM(CASE WHEN o.status = 'Refunded' THEN o.total_amount ELSE 0 END) AS refunded_amount,
            SUM(CASE WHEN o.status = 'Cancelled' THEN o.total_amount ELSE 0 END) AS cancelled_amount
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN regions r ON c.region_id = r.region_id
        GROUP BY r.region_id
    """
    return pd.read_sql(query, con=engine)
