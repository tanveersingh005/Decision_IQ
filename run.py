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
    
    args = parser.parse_args()
    
    # If no flags are passed, run everything (ETL -> ML -> App)
    run_all = not (args.only_etl or args.only_ml or args.only_app)
    
    # Setup paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    pipeline_path = os.path.join(base_dir, "etl", "pipeline.py")
    ml_path = os.path.join(base_dir, "ml", "train.py")
    app_path = os.path.join(base_dir, "python", "app.py")
    
    # 1. Run ETL
    if run_all or args.only_etl:
        print("\n--- Running ETL Pipeline & Data Warehouse Initialization ---")
        run_cmd([sys.executable, pipeline_path])
        
    # 2. Run ML Training
    if run_all or args.only_ml:
        print("\n--- Training Predictive & Forecasting ML Suite ---")
        run_cmd([sys.executable, ml_path])
        
    # 3. Launch App
    if run_all or args.only_app:
        print("\n--- Launching Streamlit Executive Dashboard ---")
        # Start Streamlit application
        # Use the current Python interpreter so this works even if the
        # streamlit executable is not available on PATH.
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], check=True)
        except KeyboardInterrupt:
            print("\nDashboard shutdown requested by user.")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("\nError: Streamlit command not found. Please ensure dependencies are installed via pip.")
            print("Try running: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
