# Deployment Guide
## Setup and Execution Manual

This guide describes how to deploy, initialize, and run the DecisionIQ Enterprise Operational Intelligence Platform on a local machine or a cloud virtual machine.

---

## 1. Prerequisites

Ensure the following tools are installed:
1.  **Python 3.9 - 3.11**
2.  **Git**
3.  **PostgreSQL** (Optional; if you wish to run the platform in database server mode instead of the default local SQLite mode)

---

## 2. Installation Steps

Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/your-org/DecisionIQ.git
cd DecisionIQ

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install required Python libraries
pip install -r requirements.txt
```

---

## 3. Execution (Quick Start)

The repository contains a unified launcher script (`run.py`) that executes the entire end-to-end data value chain with a single command:

```bash
python run.py
```

This command will:
1.  **Generate** the synthetic transactional raw dataset (seasonality, Q2 2025 anomaly, etc.).
2.  **Execute the ETL Pipeline** (`etl/pipeline.py`) to clean, validate, and load tables into the SQLite database.
3.  **Train the Machine Learning Models** (`ml/train.py`) and save `.pkl` files.
4.  **Launch the Streamlit Web Application** dashboard.

You can now open your browser and navigate to `http://localhost:8501` to interact with the executive dashboards.

---

## 4. Running with PostgreSQL

To scale DecisionIQ to an enterprise production database:

1.  **Create a database** in your PostgreSQL instance:
    ```sql
    CREATE DATABASE decision_iq;
    ```
2.  **Export the `DATABASE_URL`** environment variable before running the setup:
    ```bash
    # Linux / macOS
    export DATABASE_URL="postgresql://username:password@localhost:5432/decision_iq"

    # Windows PowerShell
    $env:DATABASE_URL="postgresql://username:password@localhost:5432/decision_iq"
    ```
3.  **Execute the launcher:**
    ```bash
    python run.py
    ```
    The DB connector will detect the PostgreSQL environment variable, initialize the schema on the server, load all records, and direct the Streamlit app to read data from PostgreSQL.

---

## 5. Verification Checklist

To verify that the deployment was successful:
*   Ensure a database file `decision_iq.db` was created in the project root (if using SQLite).
*   Verify that ML models are saved in the `ml/models/` folder:
    *   `churn_model.pkl`
    *   `revenue_forecaster.pkl`
    *   `supplier_risk_model.pkl`
    *   `training_summary.txt`
*   Ensure that the Streamlit app starts and displays the CEO overview tab with metrics and forecast charts.
