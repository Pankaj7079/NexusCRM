"""Unified ML Training Pipeline — trains 5 classifiers, picks the best, logs to MLflow."""

import os
import mlflow

from nexuscrm.core.config import settings
from nexuscrm.core.logging import logger
from nexuscrm.ml.dataset_loader import prepare_churn_data, prepare_lead_scoring_data
from nexuscrm.ml.ml_model_evaluator import model_evaluator
from nexuscrm.ml.forecasting import revenue_forecaster


def run_full_ml_pipeline():  # noqa: PLR0915
    """Train & evaluate 5 classifiers for Churn + Lead Scoring, deploy the best, and log everything to MLflow."""
    logger.info("Initializing MLflow Experiment Tracking...")
    mlflow.set_experiment(settings.LANGCHAIN_PROJECT or "nexuscrm-pro-ml")

    os.makedirs("models", exist_ok=True)

    # 1. Compare all 5 classifiers for Churn Risk Prediction
    logger.info("=== Phase 5.1: Churn Risk — Model Comparison ===")
    with mlflow.start_run(run_name="churn_model_comparison"):
        churn_results = model_evaluator.run("churn", prepare_churn_data)
        winner_name = churn_results["best_model"]
        winner_auc = churn_results["best_auc"]
        mlflow.log_param("best_churn_model", winner_name)
        mlflow.log_metric("best_churn_auc_roc", winner_auc)

    # 2. Compare all 5 classifiers for Lead Scoring Prediction
    logger.info("=== Phase 5.2: Lead Scoring — Model Comparison ===")
    with mlflow.start_run(run_name="lead_scoring_model_comparison"):
        lead_results = model_evaluator.run("lead_scoring", prepare_lead_scoring_data)
        winner_lead_name = lead_results["best_model"]
        winner_lead_auc = lead_results["best_auc"]
        mlflow.log_param("best_lead_model", winner_lead_name)
        mlflow.log_metric("best_lead_auc_roc", winner_lead_auc)

    # 3. Train Revenue Forecast Model
    logger.info("=== Phase 5.3: Training Revenue Forecast Model ===")
    with mlflow.start_run(run_name="revenue_forecast_model"):
        forecast_metrics = revenue_forecaster.train()
        mlflow.log_metrics(forecast_metrics)

    logger.info(
        f"Model comparison done.\n"
        f"  Churn  -> best: {winner_name.upper()} (AUC-ROC={winner_auc:.4f})\n"
        f"  Leads  -> best: {winner_lead_name.upper()} (AUC-ROC={winner_lead_auc:.4f})\n"
        f"  Saved to models/best_*_model.pkl — ready for inference."
    )


if __name__ == "__main__":
    run_full_ml_pipeline()
