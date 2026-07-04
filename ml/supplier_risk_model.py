import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score
import pickle
import os
import logging

logger = logging.getLogger("SupplierRiskModel")

class SupplierRiskModel:
    """
    ML Classifier to predict whether a logistics shipment will be late
    based on the supplier, destination warehouse, carrier, and product category.
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6)
        self.label_encoders = {}
        self.feature_names = []
        
    def prepare_features(self, db_engine):
        """
        Gathers shipment transactions, joins lookup details, and encodes features.
        """
        query = """
            SELECT 
                s.shipment_id,
                s.supplier_id,
                s.warehouse_id,
                s.carrier,
                s.delivery_status,
                p.category AS product_category
            FROM shipments s
            JOIN orders o ON s.order_id = o.order_id
            JOIN order_details od ON o.order_id = od.order_id
            JOIN products p ON od.product_id = p.product_id
            WHERE s.delivery_status IN ('On Time', 'Late', 'Returned')
        """
        df = pd.read_sql(query, con=db_engine)
        
        if len(df) == 0:
            raise ValueError("No shipment records found in database to train model.")
            
        # Target: 1 if Late/Returned, 0 if On Time
        df["target"] = np.where(df["delivery_status"].isin(["Late", "Returned"]), 1, 0)
        
        # Categorical columns
        cat_cols = ["supplier_id", "warehouse_id", "carrier", "product_category"]
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le
            
        self.feature_names = cat_cols
        
        return df[self.feature_names], df["target"], df
        
    def train(self, X, y):
        """
        Trains the classifier and calculates validation metrics.
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        self.model.fit(X_train, y_train)
        
        preds = self.model.predict(X_test)
        probs = self.model.predict_proba(X_test)[:, 1]
        
        roc_auc = roc_auc_score(y_test, probs)
        report = classification_report(y_test, preds, output_dict=True)
        
        logger.info(f"Supplier Delay Risk Model ROC-AUC Score: {roc_auc:.4f}")
        
        # Feature Importance
        importances = self.model.feature_importances_
        feature_importance_df = pd.DataFrame({
            "Feature": self.feature_names,
            "Importance": importances
        }).sort_values(by="Importance", ascending=False)
        
        return {
            "roc_auc": roc_auc,
            "precision": report["1"]["precision"],
            "recall": report["1"]["recall"],
            "f1_score": report["1"]["f1-score"],
            "feature_importance": feature_importance_df
        }
        
    def predict_late_probability(self, X):
        """
        Predicts late delivery probability.
        """
        return self.model.predict_proba(X)[:, 1]
        
    def save_model(self, path=None):
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "models", "supplier_risk_model.pkl"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        logger.info(f"Saved supplier risk model to {path}")
        
    @staticmethod
    def load_model(path=None):
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "models", "supplier_risk_model.pkl"))
        with open(path, "rb") as f:
            return pickle.load(f)
