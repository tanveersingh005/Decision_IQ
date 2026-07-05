import os
import sqlite3
import pandas as pd

def main():
    db_file = 'decision_iq.db'
    if not os.path.exists(db_file):
        print(f"Error: {db_file} not found. Please run the ETL pipeline first (python run.py).")
        return
        
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Save the CSVs inside a dedicated exports directory to keep your workspace clean
    export_dir = 'power_bi/csv_exports'
    os.makedirs(export_dir, exist_ok=True)
    
    print(f"Starting export of {len(tables)} tables to '{export_dir}/'...")
    for t in tables:
        table_name = t[0]
        # Skip internal sqlite metadata tables
        if table_name.startswith('sqlite_'):
            continue
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        csv_path = os.path.join(export_dir, f"{table_name}.csv")
        df.to_csv(csv_path, index=False)
        print(f"  - Exported {table_name} ({len(df)} rows) -> {csv_path}")
        
    conn.close()
    print("\nExport completed successfully! Load these CSVs from the 'power_bi/csv_exports' directory into Power BI.")

if __name__ == "__main__":
    main()
