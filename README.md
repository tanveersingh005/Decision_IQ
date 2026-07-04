# DecisionIQ: Enterprise Operational Intelligence Platform

[![Tech Stack](https://img.shields.io/badge/Stack-Python%20%7C%20Postgres%20%7C%20SQLAlchemy%20%7C%20Scikit--Learn-blue)](#tech-stack)
[![Aesthetics](https://img.shields.io/badge/Aesthetics-Consulting%20%2F%20McKinsey-gold)](#executive-aesthetics)

DecisionIQ is a production-grade enterprise analytics and operational intelligence platform designed to help business executives understand **why** performance fluctuates, identify warehouse/supplier bottlenecks, predict customer churn risks, and generate quantifiable business decisions.

It moves beyond standard dashboards to act as a **unified decision engine**, converting raw transactional rows from Sales, Finance, Operations, Logistics, and Customer Success into direct financial and operational actions.

---

## 📋 Executive Summary: The Business Scenario

### The Problem
Large organizations possess massive, siloed databases. When revenue drops:
*   The **CFO** sees a rise in refunds but cannot identify the root cause.
*   **Customer Success** notices a drop in CSAT and a rise in complaints but lacks links to logistics delays.
*   **Logistics Managers** see late shipments but don't know which suppliers or warehouses are driving contract failure.

### The Solution
DecisionIQ integrates these divisions into a normalized Star/Snowflake schema data warehouse, validates data quality using rigid range rules, builds predictive model scorecards, and deploys an automated **Insight Engine** that performs root-cause analysis:

> **Heuristic Diagnostics Alert:**
> *   **Anomalous Event:** Revenue in Q2 2025 dropped 8.5% MoM due to a spike in order refunds.
> *   **Root Cause:** Component supply delays from vendor **Apex Technology Corp** delayed hardware assembly at the **West Coast Fulfillment Center**, causing a 55% late shipment rate.
> *   **Business Impact:** Spiked Logistics tickets 3.5x, dropped CSAT to 1.8/5.0, and leaked **$245,000** in refunded bookings.
> *   **Actionable Recommendation:** Shift 40% of hardware orders to **EuroChip AG (SUP004)**, reallocate safety stock from the East Coast, and trigger proactive retention campaigns for at-risk accounts.

---

## 🛠️ Tech Stack

*   **Database:** Dual-Compatibility Connector (SQLite for local zero-config, PostgreSQL for production scaling)
*   **ORM / Database Interaction:** SQLAlchemy
*   **Data Wrangling:** Pandas & Polars
*   **Machine Learning Suite:** Scikit-Learn (Random Forest & Ridge Regression models)
*   **Interactive Visualizations:** Plotly Express & Graph Objects
*   **C-Suite Presentation:** Python Streamlit (custom styled with McKinsey/BCG design tokens)

---

## 📂 Project Structure

```
Decision_IQ/
├── sql/
│   ├── schema.sql                 # Star-schema tables, relationships & unique indexes
│   └── advanced_analytics.sql     # Advanced SQL CTEs, window functions, cohort retention
├── etl/
│   ├── generator.py               # 3-year transactional synthetic data generation
│   ├── validator.py               # Data quality audits & range rules checks
│   ├── pipeline.py                # Pipeline runner (Extract, Clean, Transform, Load)
│   └── db_connector.py            # SQLAlchemy database connection factory
├── analytics/
│   ├── metrics.py                 # C-Suite KPI (Health Score, margin, leakage) aggregations
│   └── insight_engine.py          # Operational anomaly root-cause analyzer
├── ml/
│   ├── churn_model.py             # Random Forest classifier predicting account churn
│   ├── forecasting_model.py       # Ridge Regression weekly revenue forecaster
│   ├── supplier_risk_model.py     # Logistics delay probability classifier
│   └── train.py                   # Unified ML model trainer and evaluator
├── power_bi/
│   ├── README.md                  # Layout wireframes, navigation, and theme spec
│   └── dax_reference.txt          # Production DAX measures (YoY growth, LTV, CSAT)
├── python/
│   ├── app.py                     # Streamlit C-suite Control Tower dashboard
│   └── styles.css                 # Custom CSS stylesheet injection
├── docs/
│   ├── BRD.md                     # Business Requirements Document (BRD)
│   ├── DATA_DICTIONARY.md         # Field-level database descriptions
│   ├── ARCHITECTURE.md            # Diagrammed ETL pipeline & model workflow
│   └── DEPLOYMENT_GUIDE.md        # Local & server installation manual
├── requirements.txt               # Dependencies listing
├── run.py                         # CLI script to execute pipeline, train, and open app
└── README.md                      # General platform overview
```

---

## 💡 Machine Learning & Advanced Analytics

The platform incorporates senior-level analytics modules:
1.  **Customer Churn Risk Classifier:** Predicts high-risk active accounts using support CSAT trends and order frequency.
2.  **Weekly Revenue Forecaster:** Autoregressive time-series projections modeling seasonal spikes.
3.  **Supplier delay Risk Classifier:** Identifies logistic delay risks by carrier, category, and supplier.
4.  **Advanced SQL Suite:** Features cohort matrices, RFM quintile ranking, and recursive management rollups.

---

## 🚀 Getting Started

Deploy and run the entire data and analytics suite with a single command:

```bash
# Clone and enter the project
git clone https://github.com/your-org/DecisionIQ.git
cd DecisionIQ

# Install dependencies
pip install -r requirements.txt

# Run the pipeline (generates database, trains ML models, and starts dashboard)
python run.py
```
*For detailed multi-tenant and cloud database server configurations, refer to the [Deployment Guide](file:///c:/Users/harry/OneDrive/Desktop/Decision_IQ/docs/DEPLOYMENT_GUIDE.md).*
