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

---

## 6. Deploying to Streamlit Community Cloud (Resume Portfolio)

To showcase DecisionIQ on your resume or portfolio website, you can host the interactive dashboard for free on Streamlit Community Cloud:

### Step 1: Create a GitHub Repository
1.  Initialize git in the workspace:
    ```bash
    git init
    git add .
    git commit -m "Initial commit of DecisionIQ Platform"
    ```
2.  Push this local repository to a **public GitHub repository**.
    > [!IMPORTANT]
    > **Ensure `decision_iq.db` and `ml/models/*.pkl` are committed.** 
    > By including the pre-generated database (approx 9.4MB) and the pre-trained ML model binaries directly in the repository, your live portfolio site will load the dashboard **instantly** for recruiters instead of forcing them to wait 2 minutes for initial simulation generation.

### Step 2: Set Up Streamlit Community Cloud
1.  Go to [Streamlit Community Cloud](https://share.streamlit.io/).
2.  Sign in with your GitHub account.
3.  Click **New App** in the top right.

### Step 3: Deploy the Repository
1.  Fill in the app deployment fields:
    *   **Repository:** Select your GitHub repo `username/DecisionIQ`.
    *   **Branch:** Set to `main` or `master`.
    *   **Main file path:** Set to `python/app.py`.
2.  Click **Deploy**.

Within 1-2 minutes, Streamlit will provision a container, install dependencies from `requirements.txt`, load the database, and display the operational intelligence tower. You can copy the generated URL to include in your resume or share with recruiters.

