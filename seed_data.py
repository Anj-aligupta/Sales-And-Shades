"""
seed_data.py — Generate & load synthetic sales data into SQLite
Run once before launching the app: python seed_data.py
"""

import sqlite3, random, os
from datetime import datetime, timedelta
import numpy as np

random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'data', 'sales_shades.db')

PRODUCTS = [
    (1, 'Aviator Pro X',       'PREMIUM',  4200),
    (2, 'Night Rider Cat-Eye', 'FASHION',  2800),
    (3, 'SportShield 360',     'SPORT',    3500),
    (4, 'Classic Wayfarer',    'CASUAL',   1900),
    (5, 'Kids SafeVision',     'KIDS',     1200),
    (6, 'Executive Titanium',  'PREMIUM',  6500),
    (7, 'Urban Oversized',     'FASHION',  2200),
    (8, 'Trail Blazer',        'SPORT',    2900),
]

REGIONS   = ['North', 'South', 'East', 'West', 'Export']
SEGMENTS  = ['RETAIL', 'B2B', 'WHOLESALE']
SEG_WT    = [0.55, 0.30, 0.15]
REG_WT    = [0.31, 0.21, 0.14, 0.25, 0.09]
PROD_WT   = [20, 16, 14, 11, 7, 10, 12, 10]

# Seasonal weights — Oct/Nov peak (Diwali)
MONTHLY_WT = [0.06,0.07,0.08,0.07,0.07,0.08,
              0.09,0.08,0.09,0.13,0.11,0.07]

def generate_customers(n=500):
    rows = []
    for cid in range(1, n + 1):
        seg    = random.choices(SEGMENTS, SEG_WT)[0]
        region = random.choices(REGIONS, REG_WT)[0]
        joined = datetime(2022, 1, 1) + timedelta(days=random.randint(0, 700))
        rows.append((cid, f'Customer_{cid:04d}', seg, region,
                     joined.strftime('%Y-%m-%d')))
    return rows

def generate_orders(customers, n_total=13000):
    cust_map = {c[0]: c for c in customers}
    rows, oid = [], 1
    for m_idx in range(12):
        n = int(MONTHLY_WT[m_idx] * n_total)
        for _ in range(n):
            day   = random.randint(1, 28)
            odate = datetime(2024, m_idx + 1, day).strftime('%Y-%m-%d')
            cid   = random.randint(1, len(customers))
            prod  = random.choices(PRODUCTS, PROD_WT)[0]
            qty   = random.randint(1, 5)
            disc  = random.choices([0,.05,.10,.15],[.5,.25,.15,.10])[0]
            price = prod[3]
            rev   = round(qty * price * (1 - disc), 2)
            region = cust_map[cid][3]
            ret_p  = 0.051 if region == 'South' else 0.027
            returned = 1 if random.random() < ret_p else 0
            rows.append((oid, odate, cid, prod[0],
                         qty, price, round(disc, 2), rev, returned))
            oid += 1
    return rows

def seed():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    schema = open(os.path.join(BASE_DIR, 'sql', '01_schema.sql')).read()
    for stmt in schema.split(';'):
        s = stmt.strip()
        if s:
            cur.execute(s)

    cur.execute("DELETE FROM fact_sales")
    cur.execute("DELETE FROM dim_customers")
    cur.execute("DELETE FROM dim_products")

    cur.executemany("INSERT INTO dim_products VALUES (?,?,?,?,1)", PRODUCTS)
    customers = generate_customers()
    cur.executemany("INSERT INTO dim_customers VALUES (?,?,?,?,?)", customers)
    orders = generate_orders(customers)
    cur.executemany("INSERT INTO fact_sales VALUES (?,?,?,?,?,?,?,?,?)", orders)

    conn.commit()
    conn.close()
    print(f"✓ Seeded {len(PRODUCTS)} products, "
          f"{len(customers)} customers, {len(orders)} orders")
    print(f"✓ DB → {DB_PATH}")

if __name__ == '__main__':
    seed()
