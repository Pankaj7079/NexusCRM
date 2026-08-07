"""Unified ML Model Training & MLflow Experiment Tracker."""

import os
import mlflow

from nexuscrm.core.config import settings
from nexuscrm.core.logging import logger
from nexuscrm.ml.dataset_loader import prepare_churn_data, prepare_lead_scoring_data
from nexuscrm.ml.churn_model import churn_model
from nexuscrm.ml.lead_scorer import lead_scorer
from nexuscrm.ml.forecasting import revenue_forecaster


def run_full_ml_pipeline():
    """Execute end-to-end training pipeline for Churn, Lead Scoring, and Revenue Forecast models."""
    logger.info("Initializing MLflow Experiment Tracking...")
    mlflow.set_experiment(settings.LANGCHAIN_PROJECT or "nexuscrm-pro-ml")

    os.makedirs("models", exist_ok=True)

    # 1. Train XGBoost Churn Risk Model
    logger.info("=== Phase 5.1: Training Churn Risk Model ===")
    X_train_c, X_test_c, y_train_c, y_test_c = prepare_churn_data()
    with mlflow.start_run(run_name="xgboost_churn_model"):
        churn_metrics = churn_model.train(X_train_c, y_train_c, X_test_c, y_test_c)
        mlflow.log_params({"model_type": "XGBoostClassifier", "max_depth": 4, "learning_rate": 0.05})
        mlflow.log_metrics(churn_metrics)

    # 2. Train LightGBM Lead Scoring Model
    logger.info("=== Phase 5.2: Training Lead Scoring Model ===")
    X_train_l, X_test_l, y_train_l, y_test_l = prepare_lead_scoring_data()
    with mlflow.start_run(run_name="lightgbm_lead_scorer"):
        lead_metrics = lead_scorer.train(X_train_l, y_train_l, X_test_l, y_test_l)
        mlflow.log_params({"model_type": "LGBMClassifier", "num_leaves": 31, "learning_rate": 0.05})
        mlflow.log_metrics(lead_metrics)

    # 3. Train Revenue Forecast Model
    logger.info("=== Phase 5.3: Training Revenue Forecast Model ===")
    with mlflow.start_run(run_name="revenue_forecast_model"):
        forecast_metrics = revenue_forecaster.train()
        mlflow.log_metrics(forecast_metrics)

    logger.info("All 3 ML models trained, evaluated, and saved to models/ directory successfully!")


if __name__ == "__main__":
    run_full_ml_pipeline()
