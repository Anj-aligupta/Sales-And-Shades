# Sales & Shades — Sales Data Analysis Dashboard
### Python · Dash · Plotly · pandas · SQLite | Portfolio Project

---

## What This Project Does

A full end-to-end data analyst portfolio project:

- **SQLite database** with star schema (fact + dimension tables)
- **SQL analytics queries** for EDA, KPIs, anomaly detection
- **pandas** for data cleaning and transformation
- **Dash + Plotly** for an interactive web dashboard
- **4 tabs**: Dashboard · Data Table · SQL Viewer · EDA Report

---

## Project Structure

```
sales_shades/
├── app.py                  ← Main Dash application (run this)
├── seed_data.py            ← Generates & loads data into SQLite
├── queries.py              ← All SQL queries (BI layer)
├── requirements.txt        ← Python dependencies
├── assets/
│   └── style.css           ← Dark theme styling
├── sql/
│   ├── 01_schema.sql       ← Database schema
│   └── 02_analytics_queries.sql
└── data/
    └── sales_shades.db     ← Auto-created by seed_data.py
```

---

## Setup — Step by Step

### 1. Open this folder in VS Code
```
File → Open Folder → select sales_shades/
```

### 2. Open the terminal in VS Code
```
Ctrl + ` (backtick)
```

### 3. Install dependencies
```bash
pip install dash plotly pandas numpy
```

### 4. Seed the database (run once)
```bash
python seed_data.py
```
You should see:
```
✓ Seeded 8 products, 500 customers, 13000 orders
✓ DB → data/sales_shades.db
```

### 5. Launch the app
```bash
python app.py
```

### 6. Open your browser
```
http://127.0.0.1:8050
```

---

## Dashboard Features

| Tab | What you get |
|-----|-------------|
| **Dashboard** | KPI cards, monthly trend, top products, region map, segments donut, quarterly stacked bar — all filterable |
| **Data Table** | Sortable, filterable raw orders table. Export full CSV |
| **SQL Viewer** | See every SQL query powering the charts, with live result preview |
| **EDA Report** | Auto-generated insights, anomaly detection table, correlation heatmap |

---

## Tech Stack (for your resume)

- **Python 3.12**
- **Dash 2.x** — web framework for data apps
- **Plotly** — interactive charts (bar, line, donut, heatmap, dual-axis)
- **pandas** — data cleaning, transformation
- **SQLite** — relational database with star schema
- **SQL** — JOINs, GROUP BY, HAVING, window-style aggregations
- **HTML/CSS** — custom dark theme

---

## Resume / Portfolio Description

> **Sales & Shades – Sales Data Analysis Dashboard**
> Built an end-to-end interactive sales analytics web application using Python (Dash, Plotly, pandas) and SQLite.
> Designed a star schema database, wrote SQL analytics queries for EDA, and built a multi-tab dashboard with live filters,
> export functionality, and an automated EDA report with anomaly detection.
> Tools: Python · Dash · Plotly · pandas · SQLite · SQL

---

## Common Errors

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: dash` | Run `pip install dash plotly pandas numpy` |
| `unable to open database` | Run `python seed_data.py` first |
| `Address already in use` | Change port in app.py: `app.run(port=8051)` |
| Blank page in browser | Wait 3 seconds, hard refresh (Ctrl+Shift+R) |
