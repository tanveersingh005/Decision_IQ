import sys
import os
import logging

# Adjust path to find parent modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from etl.db_connector import get_engine
from ml.churn_model import CustomerChurnModel
from ml.forecasting_model import RevenueForecaster
from ml.supplier_risk_model import SupplierRiskModel

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MLTrainingSuite")

def train_all_models():
    logger.info("=== STARTING MACHINE LEARNING MODEL TRAINING SUITE ===")
    
    engine = get_engine()
    
    # ----------------------------------------------------
    # Model 1: Customer Churn Prediction
    # ----------------------------------------------------
    logger.info("Training Customer Churn Prediction Model...")
    churn_model = CustomerChurnModel()
    X_churn, y_churn, metadata_churn = churn_model.prepare_features(engine)
    logger.info(f"Churn Model Data: {X_churn.shape[0]} customers, {X_churn.shape[1]} features.")
    
    churn_metrics = churn_model.train(X_churn, y_churn)
    churn_model.save_model()
    
    logger.info("Churn Model Feature Importance:")
    for idx, row in churn_metrics["feature_importance"].iterrows():
        logger.info(f"  - {row['Feature']}: {row['Importance']:.4f}")
        
    # ----------------------------------------------------
    # Model 2: Weekly Revenue Forecasting
    # ----------------------------------------------------
    logger.info("Training Weekly Revenue Forecaster...")
    forecaster = RevenueForecaster(lag_count=4)
    history_df = forecaster.prepare_time_series(engine)
    X_fore, y_fore, clean_history = forecaster.engineer_features(history_df)
    logger.info(f"Forecast Model Data: {X_fore.shape[0]} historical weeks, {X_fore.shape[1]} features.")
    
    forecast_metrics = forecaster.train(X_fore, y_fore)
    forecaster.save_model()
    
    # ----------------------------------------------------
    # Model 3: Supplier Shipment Delay Risk Classifier
    # ----------------------------------------------------
    logger.info("Training Supplier shipment Delay Risk Model...")
    supplier_model = SupplierRiskModel()
    X_sup, y_sup, clean_shipments = supplier_model.prepare_features(engine)
    logger.info(f"Supplier Risk Model Data: {X_sup.shape[0]} shipment-items, {X_sup.shape[1]} features.")
    
    supplier_metrics = supplier_model.train(X_sup, y_sup)
    supplier_model.save_model()
    
    logger.info("Supplier Risk Model Feature Importance:")
    for idx, row in supplier_metrics["feature_importance"].iterrows():
        logger.info(f"  - {row['Feature']}: {row['Importance']:.4f}")
        
    logger.info("=== MACHINE LEARNING TRAINING SUITE COMPLETED ===")
    
    # Save a training report summary as a text file for Power BI / analytical references
    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "models", "training_summary.txt"))
    with open(report_path, "w") as f:
        f.write("DECISIONIQ MACHINE LEARNING MODELS REPORT\n")
        f.write("=========================================\n\n")
        f.write("1. CUSTOMER CHURN MODEL (Random Forest)\n")
        f.write(f"   - ROC-AUC: {churn_metrics['roc_auc']:.4f}\n")
        f.write(f"   - Precision: {churn_metrics['precision']:.4f}\n")
        f.write(f"   - Recall: {churn_metrics['recall']:.4f}\n")
        f.write(f"   - F1-Score: {churn_metrics['f1_score']:.4f}\n\n")
        f.write("2. WEEKLY REVENUE FORECASTER (Ridge Autoregression)\n")
        f.write(f"   - Mean Absolute Error (MAE): ${forecast_metrics['mae']:,.2f}\n")
        f.write(f"   - Mean Absolute Percentage Error (MAPE): {forecast_metrics['mape']:.2f}%\n")
        f.write(f"   - R-squared (R2) Score: {forecast_metrics['r2']:.4f}\n\n")
        f.write("3. SUPPLIER DELAY RISK MODEL (Random Forest)\n")
        f.write(f"   - ROC-AUC: {supplier_metrics['roc_auc']:.4f}\n")
        f.write(f"   - Precision: {supplier_metrics['precision']:.4f}\n")
        f.write(f"   - Recall: {supplier_metrics['recall']:.4f}\n")
        f.write(f"   - F1-Score: {supplier_metrics['f1_score']:.4f}\n")
        
    logger.info(f"Training summary report exported to {report_path}")

if __name__ == "__main__":
    train_all_models()
