import sys
import os
import pandas as pd
import logging
from datetime import datetime

# Adjust path to find other modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from etl.generator import generate_synthetic_data
from etl.validator import ETLValidator
from etl.db_connector import get_engine, init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ETLPipeline")

def run_etl_pipeline():
    logger.info("=== STARTING DECISIONIQ ETL PIPELINE ===")
    
    # ----------------------------------------------------
    # 1. EXTRACT
    # ----------------------------------------------------
    logger.info("Step 1: Extracting raw data from synthetic generator...")
    dfs = generate_synthetic_data()
    
    # ----------------------------------------------------
    # 2. VALIDATE & CLEAN (Intermediate validation on raw data)
    # ----------------------------------------------------
    logger.info("Step 2: Cleaning and validating data tables...")
    
    # --- CLEAN CUSTOMERS ---
    customers_raw = dfs["customers"]
    logger.info(f"Initial customers count: {len(customers_raw)}")
    
    # Deduplicate customers by email address, keeping the earliest acquisition date
    customers_raw = customers_raw.sort_values(by="acquisition_date")
    
    # Create mapping of duplicate customer IDs to their master (first kept) customer ID
    is_duplicate = customers_raw.duplicated(subset=["contact_email"], keep="first")
    master_records = customers_raw[~is_duplicate][["contact_email", "customer_id"]].rename(columns={"customer_id": "master_customer_id"})
    duplicate_records = customers_raw[is_duplicate][["contact_email", "customer_id"]]
    mapping_df = duplicate_records.merge(master_records, on="contact_email", how="left")
    customer_id_map = dict(zip(mapping_df["customer_id"], mapping_df["master_customer_id"]))
    
    customers_clean = customers_raw.drop_duplicates(subset=["contact_email"], keep="first")
    logger.info(f"Deduplicated customers count: {len(customers_clean)}")
    
    # Clean whitespace and normalize text
    customers_clean = customers_clean.copy()
    customers_clean["company_name"] = customers_clean["company_name"].str.strip()
    customers_clean["contact_name"] = customers_clean["contact_name"].str.strip()
    customers_clean["customer_segment"] = customers_clean["customer_segment"].str.upper().str.strip()
    
    # --- CLEAN PRODUCTS ---
    products_clean = dfs["products"].copy()
    products_clean["product_name"] = products_clean["product_name"].str.strip()
    products_clean["sku"] = products_clean["sku"].str.upper().str.strip()
    
    # --- CLEAN ORDERS ---
    orders_clean = dfs["orders"].copy()
    orders_clean["status"] = orders_clean["status"].str.capitalize().str.strip()
    
    # Map customer references in child tables
    if customer_id_map:
        logger.info(f"Mapping {len(customer_id_map)} duplicate customer accounts to Golden Master Records in orders and support tickets...")
        orders_clean["customer_id"] = orders_clean["customer_id"].replace(customer_id_map)
        dfs["customer_support"]["customer_id"] = dfs["customer_support"]["customer_id"].replace(customer_id_map)
        
    # Replace the dict values back
    dfs["customers"] = customers_clean
    dfs["products"] = products_clean
    dfs["orders"] = orders_clean
    
    # ----------------------------------------------------
    # 3. TRANSFORM & FEATURE ENGINEERING
    # ----------------------------------------------------
    logger.info("Step 3: Transforming data and engineering features...")
    
    # Feature 1: Add unit_cost and margins directly to order details for easy SQL aggregation
    order_details_merged = dfs["order_details"].merge(
        products_clean[["product_id", "unit_cost"]],
        on="product_id",
        how="left"
    )
    
    # We can calculate the total cost and profit margin for the detail rows
    # Note: unit_cost is used for margin analysis in downstream models
    
    # ----------------------------------------------------
    # 4. RUN SYSTEMIC DATA QUALITY CHECKS
    # ----------------------------------------------------
    logger.info("Step 4: Executing enterprise data quality audits...")
    validation_status = True
    
    # Primary Key Validations
    validation_status &= ETLValidator.validate_pk(dfs["regions"], "regions", "region_id")
    validation_status &= ETLValidator.validate_pk(dfs["employees"], "employees", "employee_id")
    validation_status &= ETLValidator.validate_pk(dfs["customers"], "customers", "customer_id")
    validation_status &= ETLValidator.validate_pk(dfs["products"], "products", "product_id")
    validation_status &= ETLValidator.validate_pk(dfs["warehouses"], "warehouses", "warehouse_id")
    validation_status &= ETLValidator.validate_pk(dfs["suppliers"], "suppliers", "supplier_id")
    validation_status &= ETLValidator.validate_pk(dfs["orders"], "orders", "order_id")
    validation_status &= ETLValidator.validate_pk(dfs["payments"], "payments", "payment_id")
    validation_status &= ETLValidator.validate_pk(dfs["shipments"], "shipments", "shipment_id")
    validation_status &= ETLValidator.validate_pk(dfs["marketing_campaigns"], "marketing_campaigns", "campaign_id")
    validation_status &= ETLValidator.validate_pk(dfs["customer_support"], "customer_support", "ticket_id")
    validation_status &= ETLValidator.validate_pk(dfs["daily_business_metrics"], "daily_business_metrics", "metric_date")
    
    # Range Validations
    validation_status &= ETLValidator.validate_ranges(dfs["products"], "products", {"unit_price": (0, None), "unit_cost": (0, None)})
    validation_status &= ETLValidator.validate_ranges(dfs["orders"], "orders", {"total_amount": (0, None)})
    validation_status &= ETLValidator.validate_ranges(dfs["order_details"], "order_details", {"quantity": (1, None), "unit_price": (0, None), "discount_amount": (0, None), "subtotal": (0, None)})
    validation_status &= ETLValidator.validate_ranges(dfs["suppliers"], "suppliers", {"lead_time_days": (0, None), "reliability_score": (0.0, 1.0)})
    validation_status &= ETLValidator.validate_ranges(dfs["customer_support"], "customer_support", {"satisfaction_score": (1, 5)})
    
    # Referential Integrity (Foreign Keys)
    validation_status &= ETLValidator.validate_fk(dfs["employees"], "employees", "region_id", dfs["regions"], "regions", "region_id")
    validation_status &= ETLValidator.validate_fk(dfs["customers"], "customers", "region_id", dfs["regions"], "regions", "region_id")
    validation_status &= ETLValidator.validate_fk(dfs["warehouses"], "warehouses", "region_id", dfs["regions"], "regions", "region_id")
    validation_status &= ETLValidator.validate_fk(dfs["inventory"], "inventory", "warehouse_id", dfs["warehouses"], "warehouses", "warehouse_id")
    validation_status &= ETLValidator.validate_fk(dfs["inventory"], "inventory", "product_id", dfs["products"], "products", "product_id")
    validation_status &= ETLValidator.validate_fk(dfs["orders"], "orders", "customer_id", dfs["customers"], "customers", "customer_id")
    validation_status &= ETLValidator.validate_fk(dfs["orders"], "orders", "sales_representative_id", dfs["employees"], "employees", "employee_id")
    validation_status &= ETLValidator.validate_fk(dfs["order_details"], "order_details", "order_id", dfs["orders"], "orders", "order_id")
    validation_status &= ETLValidator.validate_fk(dfs["order_details"], "order_details", "product_id", dfs["products"], "products", "product_id")
    validation_status &= ETLValidator.validate_fk(dfs["payments"], "payments", "order_id", dfs["orders"], "orders", "order_id")
    validation_status &= ETLValidator.validate_fk(dfs["shipments"], "shipments", "order_id", dfs["orders"], "orders", "order_id")
    validation_status &= ETLValidator.validate_fk(dfs["shipments"], "shipments", "warehouse_id", dfs["warehouses"], "warehouses", "warehouse_id")
    validation_status &= ETLValidator.validate_fk(dfs["shipments"], "shipments", "supplier_id", dfs["suppliers"], "suppliers", "supplier_id")
    validation_status &= ETLValidator.validate_fk(dfs["customer_support"], "customer_support", "customer_id", dfs["customers"], "customers", "customer_id")
    validation_status &= ETLValidator.validate_fk(dfs["customer_support"], "customer_support", "agent_id", dfs["employees"], "employees", "employee_id")
    
    if not validation_status:
        logger.error("ETL Validation Failed. Stopping ETL process.")
        raise ValueError("Data validation errors detected.")
        
    logger.info("All data quality checks completed successfully. Process proceeding to database loading.")
    
    # ----------------------------------------------------
    # 5. LOAD
    # ----------------------------------------------------
    logger.info("Step 5: Resetting and initializing database schemas...")
    init_db()
    
    logger.info("Loading cleaned tables into the data warehouse...")
    engine = get_engine()
    
    # Bulk loading tables in order of dependency (parent tables first)
    load_order = [
        ("regions", dfs["regions"]),
        ("employees", dfs["employees"]),
        ("customers", dfs["customers"]),
        ("products", dfs["products"]),
        ("warehouses", dfs["warehouses"]),
        ("suppliers", dfs["suppliers"]),
        ("inventory", dfs["inventory"]),
        ("marketing_campaigns", dfs["marketing_campaigns"]),
        ("orders", dfs["orders"]),
        ("order_details", dfs["order_details"]),
        ("payments", dfs["payments"]),
        ("shipments", dfs["shipments"]),
        ("customer_support", dfs["customer_support"]),
        ("daily_business_metrics", dfs["daily_business_metrics"]),
        ("scenario_metadata", dfs["scenario_metadata"])
    ]
    
    with engine.begin() as connection:
        for table_name, df in load_order:
            logger.info(f"Loading table '{table_name}' ({len(df)} rows)...")
            # We use SQLAlchemy to append data since tables were initialized by init_db
            df.to_sql(table_name, con=connection, if_exists="append", index=False)
            
    logger.info("=== ETL PIPELINE COMPLETED SUCCESSFULLY ===")
    logger.info("Database loaded, constraints and index structures are active.")

if __name__ == "__main__":
    run_etl_pipeline()
