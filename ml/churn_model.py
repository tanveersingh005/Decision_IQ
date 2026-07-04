import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, roc_auc_score
import pickle
import os
import logging

logger = logging.getLogger("ChurnModel")

class CustomerChurnModel:
    """
    ML Classifier to identify customers at risk of churn.
    Uses RFM features, support ticket history, and satisfaction ratings.
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8)
        self.label_encoders = {}
        self.feature_names = []
        
    def prepare_features(self, db_engine):
        """
        Extracts raw tables and builds the feature matrix for churn prediction.
        """
        # Load customers
        customers = pd.read_sql("SELECT * FROM customers", con=db_engine)
        
        # Calculate Order Metrics
        orders = pd.read_sql("SELECT * FROM orders", con=db_engine)
        # Filter successful orders for RFM
        success_orders = orders[~orders["status"].isin(["Cancelled"])]
        
        # Calculate recency, frequency, monetary
        # Set database max date as reference point
        max_date = success_orders["order_date"].max()
        if pd.isna(max_date):
            max_date = pd.Timestamp.now().date()
        else:
            max_date = pd.to_datetime(max_date).date()
            
        success_orders = success_orders.copy()
        success_orders["order_date"] = pd.to_datetime(success_orders["order_date"])
        
        order_metrics = success_orders.groupby("customer_id").agg(
            recency_days=("order_date", lambda x: (max_date - x.max().date()).days),
            frequency=("order_id", "count"),
            monetary_value=("total_amount", "sum"),
            avg_order_value=("total_amount", "mean")
        ).reset_index()
        
        # Calculate Support Metrics
        support = pd.read_sql("SELECT * FROM customer_support", con=db_engine)
        support_metrics = support.groupby("customer_id").agg(
            ticket_count=("ticket_id", "count"),
            avg_csat=("satisfaction_score", "mean")
        ).reset_index()
        # Handle customers with no support tickets (fill CSAT with neutral 4.0, count with 0)
        support_metrics["avg_csat"] = support_metrics["avg_csat"].fillna(4.0)
        
        # Merge all features together
        features = customers.merge(order_metrics, on="customer_id", how="left")
        features = features.merge(support_metrics, on="customer_id", how="left")
        
        # Fill missing values for customers with no orders
        features["recency_days"] = features["recency_days"].fillna(365) # 1 year ago
        features["frequency"] = features["frequency"].fillna(0)
        features["monetary_value"] = features["monetary_value"].fillna(0)
        features["avg_order_value"] = features["avg_order_value"].fillna(0)
        features["ticket_count"] = features["ticket_count"].fillna(0)
        features["avg_csat"] = features["avg_csat"].fillna(4.0)
        
        # Define target variable: Churned or At-Risk = 1, Active = 0
        features["target"] = np.where(features["status"].isin(["Churned", "At-Risk"]), 1, 0)
        
        # Categorical columns to encode
        cat_cols = ["customer_segment", "region_id", "acquisition_channel"]
        for col in cat_cols:
            le = LabelEncoder()
            features[col] = le.fit_transform(features[col].astype(str))
            self.label_encoders[col] = le
            
        self.feature_names = cat_cols + ["recency_days", "frequency", "monetary_value", "avg_order_value", "ticket_count", "avg_csat"]
        
        return features[self.feature_names], features["target"], features[["customer_id", "company_name"]]
        
    def train(self, X, y):
        """
        Splits data, trains the Random Forest classifier, and evaluates performance.
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        self.model.fit(X_train, y_train)
        
        # Evaluate
        preds = self.model.predict(X_test)
        probs = self.model.predict_proba(X_test)[:, 1]
        
        roc_auc = roc_auc_score(y_test, probs)
        report = classification_report(y_test, preds, output_dict=True)
        
        logger.info(f"Churn Model ROC-AUC Score: {roc_auc:.4f}")
        logger.info(f"Churn Model Precision: {report['1']['precision']:.4f} | Recall: {report['1']['recall']:.4f}")
        
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
        
    def predict_churn_risk(self, X):
        """
        Returns the churn probability for a given feature matrix.
        """
        return self.model.predict_proba(X)[:, 1]
        
    def save_model(self, path=None):
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "models", "churn_model.pkl"))
            
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        logger.info(f"Saved churn model to {path}")
        
    @staticmethod
    def load_model(path=None):
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "models", "churn_model.pkl"))
        with open(path, "rb") as f:
            return pickle.load(f)
