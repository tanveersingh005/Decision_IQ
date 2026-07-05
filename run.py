import argparse
import subprocess
import sys
import os
import time

def run_cmd(args):
    """
    Executes a shell command.
    """
    print(f"Executing: {' '.join(args)}")
    res = subprocess.run(args, capture_output=False, text=True)
    if res.returncode != 0:
        print(f"Error executing command: {' '.join(args)}")
        sys.exit(res.returncode)

def main():
    parser = argparse.ArgumentParser(description="DecisionIQ Enterprise Operational Intelligence Launcher")
    parser.add_argument("--only-etl", action="store_true", help="Only run raw data generation and ETL pipeline")
    parser.add_argument("--only-ml", action="store_true", help="Only train machine learning models")
    parser.add_argument("--only-app", action="store_true", help="Only launch Streamlit dashboard app")
    parser.add_argument("--force-etl", action="store_true", help="Force rebuild of database and ML retraining")
    
    args = parser.parse_args()
    
    # Setup paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(base_dir)
    
    pipeline_path = os.path.join(base_dir, "etl", "pipeline.py")
    ml_path = os.path.join(base_dir, "ml", "train.py")
    app_path = os.path.join(base_dir, "python", "app.py")
    db_path = os.path.join(base_dir, "decision_iq.db")
    
    run_all = not (args.only_etl or args.only_ml or args.only_app)
    
    db_exists = os.path.exists(db_path)
    
    # Check if the database has outdated scenario_metadata schema
    if db_exists:
        try:
            from etl.db_connector import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.begin() as conn:
                conn.execute(text("SELECT active_status FROM scenario_metadata LIMIT 1"))
        except Exception:
            print("\nOutdated database schema detected. Forcing database reset and migration...")
            args.force_etl = True
            
    # 1. Run ETL
    if args.only_etl:
        print("\n--- Running ETL Pipeline & Data Warehouse Initialization ---")
        run_cmd([sys.executable, pipeline_path])
    elif run_all and (not db_exists or args.force_etl):
        print("\n--- Initializing Enterprise Data Warehouse & Active Scenario ---")
        # Import and trigger via ScenarioManager to ensure active scenario is stored
        from etl.scenario_manager import ScenarioManager
        ScenarioManager.generate_new_scenario()
    elif run_all and db_exists:
        print("\nDatabase exists. Skipping data generation and ETL pipeline.")
        
    # 2. Run ML Training
    if args.only_ml:
        print("\n--- Training Predictive & Forecasting ML Suite ---")
        run_cmd([sys.executable, ml_path])
    elif run_all and (not db_exists or args.force_etl):
        # Already handled by ScenarioManager.generate_new_scenario() above
        pass
    elif run_all and db_exists:
        print("Database exists. Skipping ML models retraining.")
        
    # 3. Launch App
    if run_all or args.only_app:
        print("\n--- Launching Streamlit Executive Dashboard ---")
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], check=True)
        except KeyboardInterrupt:
            print("\nDashboard shutdown requested by user.")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("\nError: Streamlit command not found. Please ensure dependencies are installed via pip.")
            print("Try running: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
