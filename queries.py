"""
queries.py — All SQL queries centralised (mirrors real MNC BI layer)
The Dash app calls these functions; never writes SQL inline.
"""

import sqlite3, os
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'data', 'sales_shades.db')

def _conn():
    return sqlite3.connect(DB_PATH)

# ── RAW SQL strings (shown in the SQL Viewer tab) ──────────
SQL_MONTHLY = """
SELECT
    strftime('%Y-%m', order_date)        AS month,
    strftime('%m', order_date)           AS month_num,
    COUNT(DISTINCT order_id)             AS total_orders,
    ROUND(SUM(revenue) / 100000.0, 2)   AS revenue_lakhs,
    ROUND(AVG(revenue), 0)              AS avg_order_value,
    SUM(is_returned)                     AS returns,
    ROUND(SUM(is_returned)*100.0 /
          COUNT(order_id), 2)            AS return_rate
FROM  fact_sales
WHERE strftime('%Y', order_date) = '2024'
GROUP BY month
ORDER BY month;
"""

SQL_PRODUCTS = """
SELECT
    p.product_name,
    p.category,
    COUNT(s.order_id)                    AS orders,
    SUM(s.quantity)                      AS units_sold,
    ROUND(SUM(s.revenue)/100000.0, 2)   AS revenue_lakhs,
    ROUND(AVG(s.discount_pct)*100, 1)   AS avg_discount_pct,
    ROUND(SUM(s.revenue)*100.0 /
         (SELECT SUM(revenue) FROM fact_sales), 2) AS revenue_share_pct
FROM  fact_sales s
JOIN  dim_products p ON s.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue_lakhs DESC;
"""

SQL_SEGMENTS = """
SELECT
    c.segment,
    COUNT(DISTINCT c.customer_id)       AS customers,
    COUNT(s.order_id)                   AS orders,
    ROUND(SUM(s.revenue)/100000.0, 2)  AS revenue_lakhs,
    ROUND(AVG(s.revenue), 0)           AS avg_order_value
FROM  fact_sales s
JOIN  dim_customers c ON s.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY revenue_lakhs DESC;
"""

SQL_REGIONS = """
SELECT
    c.region,
    COUNT(s.order_id)                   AS orders,
    ROUND(SUM(s.revenue)/100000.0, 2)  AS revenue_lakhs,
    ROUND(SUM(s.is_returned)*100.0 /
          COUNT(s.order_id), 2)         AS return_rate
FROM  fact_sales s
JOIN  dim_customers c ON s.customer_id = c.customer_id
GROUP BY c.region
ORDER BY revenue_lakhs DESC;
"""

SQL_ANOMALIES = """
SELECT
    c.region,
    p.category,
    COUNT(s.order_id)                   AS orders,
    SUM(s.is_returned)                  AS returns,
    ROUND(SUM(s.is_returned)*100.0 /
          COUNT(s.order_id), 2)         AS return_rate
FROM  fact_sales s
JOIN  dim_customers c ON s.customer_id = c.customer_id
JOIN  dim_products  p ON s.product_id  = p.product_id
GROUP BY c.region, p.category
HAVING return_rate > 4.0
ORDER BY return_rate DESC;
"""

SQL_QUARTERLY = """
SELECT
    ('Q' || ((CAST(strftime('%m', order_date) AS INTEGER) - 1) / 3 + 1))
                                        AS quarter,
    p.category,
    ROUND(SUM(s.revenue)/100000.0, 2)  AS revenue_lakhs
FROM  fact_sales s
JOIN  dim_products p ON s.product_id = p.product_id
WHERE strftime('%Y', order_date) = '2024'
GROUP BY quarter, p.category
ORDER BY quarter, revenue_lakhs DESC;
"""

SQL_CORR = """
SELECT
    strftime('%Y-%m', order_date)       AS month,
    ROUND(SUM(revenue)/100000.0, 2)    AS revenue_lakhs,
    COUNT(DISTINCT order_id)            AS orders,
    ROUND(AVG(revenue), 0)             AS avg_order_value,
    SUM(is_returned)                    AS returns,
    ROUND(AVG(discount_pct)*100, 2)    AS avg_discount
FROM  fact_sales
GROUP BY month
ORDER BY month;
"""

SQL_CATALOG = {
    "Monthly Revenue Trend":    SQL_MONTHLY,
    "Top Products":             SQL_PRODUCTS,
    "Customer Segments":        SQL_SEGMENTS,
    "Regional Breakdown":       SQL_REGIONS,
    "Return Rate Anomalies":    SQL_ANOMALIES,
    "Quarterly by Category":    SQL_QUARTERLY,
    "KPI Correlation Data":     SQL_CORR,
}

# ── Data fetchers ──────────────────────────────────────────
def get_monthly():
    return pd.read_sql(SQL_MONTHLY, _conn())

def get_products():
    return pd.read_sql(SQL_PRODUCTS, _conn())

def get_segments():
    return pd.read_sql(SQL_SEGMENTS, _conn())

def get_regions():
    return pd.read_sql(SQL_REGIONS, _conn())

def get_anomalies():
    return pd.read_sql(SQL_ANOMALIES, _conn())

def get_quarterly():
    return pd.read_sql(SQL_QUARTERLY, _conn())

def get_corr_data():
    return pd.read_sql(SQL_CORR, _conn())

def get_kpis():
    df = get_monthly()
    return {
        'revenue':    round(df['revenue_lakhs'].sum(), 1),
        'orders':     int(df['total_orders'].sum()),
        'aov':        int(df['avg_order_value'].mean()),
        'return_rate':round(df['return_rate'].mean(), 2),
    }

def get_raw_table(limit=200):
    sql = f"""
    SELECT s.order_id, s.order_date,
           p.product_name, p.category,
           c.segment, c.region,
           s.quantity, s.unit_price,
           ROUND(s.discount_pct*100,0) AS discount_pct,
           s.revenue,
           CASE s.is_returned WHEN 1 THEN 'Yes' ELSE 'No' END AS returned
    FROM   fact_sales s
    JOIN   dim_products  p ON s.product_id  = p.product_id
    JOIN   dim_customers c ON s.customer_id = c.customer_id
    ORDER  BY s.order_date DESC
    LIMIT  {limit};
    """
    return pd.read_sql(sql, _conn())
