import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import os
import logging

logger = logging.getLogger("ForecastingModel")

class RevenueForecaster:
    """
    ML Autoregressive model to forecast future enterprise weekly revenue.
    Engineers trend, calendar seasonality, and lag/rolling features.
    """
    
    def __init__(self, lag_count=4):
        self.model = Ridge(alpha=1.0)
        self.lag_count = lag_count
        self.last_known_data = None
        
    def prepare_time_series(self, db_engine):
        """
        Aggregates orders to weekly revenue data.
        """
        orders = pd.read_sql("SELECT order_date, total_amount FROM orders WHERE status NOT IN ('Cancelled')", con=db_engine)
        orders["order_date"] = pd.to_datetime(orders["order_date"])
        
        # Resample to weekly frequency
        weekly_rev = orders.set_index("order_date").resample("W-MON")["total_amount"].sum().reset_index()
        weekly_rev.columns = ["ds", "y"]
        
        # Sort values
        weekly_rev = weekly_rev.sort_values(by="ds").reset_index(drop=True)
        return weekly_rev
        
    def engineer_features(self, df):
        """
        Creates lags, rolling averages, trend, and week-of-year seasonality.
        """
        df = df.copy()
        
        # Trend
        df["trend"] = np.arange(len(df))
        
        # Calendar Seasonality
        df["week_of_year"] = df["ds"].dt.isocalendar().week.astype(float)
        df["month_of_year"] = df["ds"].dt.month.astype(float)
        
        # Create lags
        for i in range(1, self.lag_count + 1):
            df[f"lag_{i}"] = df["y"].shift(i)
            
        # Create rolling averages
        df["rolling_mean_4w"] = df["y"].shift(1).rolling(window=4).mean()
        
        # Drop rows with NaN (due to shifting/rolling)
        df_clean = df.dropna().reset_index(drop=True)
        
        feature_cols = ["trend", "week_of_year", "month_of_year"] + [f"lag_{i}" for i in range(1, self.lag_count + 1)] + ["rolling_mean_4w"]
        
        return df_clean[feature_cols], df_clean["y"], df_clean
        
    def train(self, X, y):
        """
        Splits chronologically (time-series split) and trains Ridge regression.
        """
        # Time-series split (last 12 weeks for testing)
        test_size = 12
        X_train, X_test = X.iloc[:-test_size], X.iloc[-test_size:]
        y_train, y_test = y.iloc[:-test_size], y.iloc[-test_size:]
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        preds = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        
        # Calculate mean absolute percentage error
        mape = np.mean(np.abs((y_test - preds) / y_test)) * 100.0
        
        logger.info(f"Weekly Revenue Forecast - MAE: ${mae:,.2f} | MAPE: {mape:.2f}% | R2 Score: {r2:.4f}")
        
        # Refit on all historical data
        self.model.fit(X, y)
        
        return {
            "mae": mae,
            "mape": mape,
            "r2": r2,
            "coefficients": dict(zip(X.columns, self.model.coef_))
        }
        
    def forecast_future(self, history_df, steps=12):
        """
        Performs recursive multi-step forecasting for future weeks.
        """
        predictions = []
        future_dates = []
        
        # Work on a copy of the tail of the history to simulate recursive lags
        # We need enough rows to calculate lag and rolling features
        sim_data = history_df.copy()
        
        last_row = sim_data.iloc[-1]
        last_date = last_row["ds"]
        trend_val = last_row["trend"]
        
        current_idx = len(sim_data)
        
        for step in range(1, steps + 1):
            next_date = last_date + timedelta(weeks=step)
            trend_val += 1
            week_of_year = float(next_date.isocalendar()[1])
            month_of_year = float(next_date.month)
            
            # Retrieve lags recursively from sim_data
            lags = []
            for i in range(1, self.lag_count + 1):
                lags.append(sim_data.iloc[-i]["y"])
                
            rolling_4w = sim_data.iloc[-4:]["y"].mean()
            
            # Feature Vector
            feats = [trend_val, week_of_year, month_of_year] + lags + [rolling_4w]
            feats_df = pd.DataFrame([feats], columns=["trend", "week_of_year", "month_of_year"] + [f"lag_{i}" for i in range(1, self.lag_count + 1)] + ["rolling_mean_4w"])
            
            # Predict
            pred_y = float(self.model.predict(feats_df)[0])
            pred_y = max(0.0, pred_y) # Revenue cannot be negative
            
            predictions.append(pred_y)
            future_dates.append(next_date)
            
            # Append new prediction to sim_data for next iteration lags
            new_row = {
                "ds": next_date,
                "y": pred_y,
                "trend": trend_val,
                "week_of_year": week_of_year,
                "month_of_year": month_of_year
            }
            # Fill lags for bookkeeping (though we query index directly)
            for i in range(1, self.lag_count + 1):
                new_row[f"lag_{i}"] = sim_data.iloc[-i]["y"]
            new_row["rolling_mean_4w"] = rolling_4w
            
            sim_data = pd.concat([sim_data, pd.DataFrame([new_row])], ignore_index=True)
            
        return pd.DataFrame({
            "ds": future_dates,
            "y_forecast": predictions
        })
        
    def save_model(self, path=None):
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "models", "revenue_forecaster.pkl"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        logger.info(f"Saved forecaster model to {path}")
        
    @staticmethod
    def load_model(path=None):
        if path is None:
            path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml", "models", "revenue_forecaster.pkl"))
        with open(path, "rb") as f:
            return pickle.load(f)

# Helper function
from datetime import timedelta
