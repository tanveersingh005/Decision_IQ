import os
import random
import logging
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from etl.db_connector import get_engine, DEFAULT_DB_PATH
from etl.pipeline import run_etl_pipeline
from ml.train import train_all_models

logger = logging.getLogger("ScenarioManager")

class ScenarioManager:
    SCENARIO_TYPES = {
        "SUPPLY_CHAIN_CRISIS": ("Supply Chain Crisis", "Apex supplier lead-time delays coupled with West Coast warehouse understaffing causing NA regional refund spike."),
        "MARKETING_INEFFICIENCY": ("Marketing Campaign Failure", "High social media ad budgets failing to convert, driving CAC spikes and low ROAS."),
        "CUSTOMER_CHURN_SURGE": ("Customer Churn Surge", "Support desk ticket resolution backlogs leading to a drop in CSAT and elevated SMB account cancellations."),
        "INVENTORY_OVERSTOCK": ("Inventory Overstock", "Over-purchasing hardware stock relative to sales drop, causing emergency warehouse operating costs to double."),
        "REGIONAL_SALES_COLLAPSE": ("Regional Sales Collapse", "An abrupt sales drop in the European region due to competitive market pricing adjustments."),
        "CASH_FLOW_CRISIS": ("Cash Flow Crisis", "Payment processing failures and wire transfer delays impacting liquidity and net margin settlements."),
        "DEMAND_SPIKE": ("Demand Spike", "An unexpected spike in software license orders outstripping supporting consulting capacity."),
        "SUPPLIER_RELIABILITY_CRISIS": ("Supplier Reliability Crisis", "Deteriorated supplier scores across multiple providers causing localized assembly issues."),
        "SUPPORT_BACKLOG": ("Support Backlog", "A surge in billing inquiries causing support queue delays and lower customer satisfaction."),
        "PRODUCT_RECALL": ("Product Recall", "A hardware defect in the network switch lines forcing order cancellations and refunds."),
        "WAREHOUSE_CONGESTION": ("Warehouse Congestion", "EMEA central depot capacity constraint slowing shipping carrier dispatches."),
        "SEASONAL_HOLIDAY_DEMAND": ("Seasonal Holiday Demand", "Q4 demand spike straining supply chain logistics with carrier bottlenecks.")
    }

    @staticmethod
    def db_exists() -> bool:
        return os.path.exists(DEFAULT_DB_PATH)

    @staticmethod
    def get_active_scenario() -> dict:
        """
        Retrieves the active scenario metadata from the database.
        """
        if not ScenarioManager.db_exists():
            return {}
        engine = get_engine()
        query = "SELECT * FROM scenario_metadata WHERE active_status = 'Active' ORDER BY generated_timestamp DESC LIMIT 1"
        try:
            df = pd.read_sql(query, con=engine)
            if not df.empty:
                return df.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Failed to fetch active scenario: {e}")
        return {}

    @staticmethod
    def get_scenario_history() -> list:
        """
        Retrieves historical scenarios from the database.
        """
        if not ScenarioManager.db_exists():
            return []
        engine = get_engine()
        query = "SELECT * FROM scenario_metadata ORDER BY generated_timestamp DESC"
        try:
            df = pd.read_sql(query, con=engine)
            if not df.empty:
                return df.to_dict(orient="records")
        except Exception as e:
            logger.error(f"Failed to fetch scenario history: {e}")
        return []

    @staticmethod
    def generate_new_scenario(scenario_key: str = None) -> dict:
        """
        Generates a new scenario by:
        1. Determining scenario name and metadata.
        2. Set environmental override.
        3. Triggering ETL pipeline to regenerate data.
        4. Inserting metadata into scenario_metadata table.
        5. Retraining ML models.
        """
        # Pick a random scenario if not specified
        if not scenario_key or scenario_key not in ScenarioManager.SCENARIO_TYPES:
            scenario_key = random.choice(list(ScenarioManager.SCENARIO_TYPES.keys()))
            
        name, desc = ScenarioManager.SCENARIO_TYPES[scenario_key]
        
        # Calculate new scenario ID (e.g. SCN-XXXXX)
        history = ScenarioManager.get_scenario_history()
        next_num = len(history) + 1
        scenario_id = f"SCN-{next_num:05d}"
        
        # Check if the database has outdated scenario_metadata schema
        if ScenarioManager.db_exists():
            from sqlalchemy import text
            engine = get_engine()
            try:
                with engine.begin() as conn:
                    conn.execute(text("SELECT active_status FROM scenario_metadata LIMIT 1"))
            except Exception:
                logger.warning("Detected outdated scenario_metadata table. Dropping it for migration.")
                try:
                    with engine.begin() as conn:
                        conn.execute(text("DROP TABLE IF EXISTS scenario_metadata"))
                except Exception as drop_err:
                    logger.error(f"Failed to drop outdated scenario_metadata table: {drop_err}")
                    
        # Override scenario in environment variable for the generator
        os.environ["SIMULATION_SCENARIO"] = scenario_key
        
        logger.info(f"Generating new scenario {scenario_id}: {name} ({scenario_key})...")
        
        # Trigger ETL pipeline (which runs init_db to reset tables but preserves scenario_metadata)
        run_etl_pipeline()
        
        # Insert metadata
        engine = get_engine()
        insert_query = text("""
            INSERT INTO scenario_metadata (
                scenario_id, scenario_name, scenario_type, seed_value, scenario_description, active_status
            ) VALUES (
                :scenario_id, :scenario_name, :scenario_type, :seed_value, :scenario_description, 'Active'
            )
        """)
        
        try:
            with engine.begin() as connection:
                # Mark previous active status as Historical
                connection.execute(text("UPDATE scenario_metadata SET active_status = 'Historical'"))
                connection.execute(insert_query, {
                    "scenario_id": scenario_id,
                    "scenario_name": name,
                    "scenario_type": scenario_key,
                    "seed_value": 42,
                    "scenario_description": desc
                })
            logger.info(f"Inserted metadata for scenario {scenario_id} ({name}).")
        except Exception as e:
            logger.error(f"Failed to save scenario metadata: {e}")
            
        # Trigger ML model retraining
        logger.info("Retraining ML models for the new scenario data...")
        train_all_models()
        
        return {
            "scenario_id": scenario_id,
            "scenario_name": name,
            "scenario_type": scenario_key,
            "scenario_description": desc
        }
