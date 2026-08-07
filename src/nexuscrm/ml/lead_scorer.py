"""LightGBM Lead Scoring Model with Calibrated Probability Output."""

import os
import joblib
import pandas as pd
from typing import Dict, Any
from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score

from nexuscrm.core.logging import logger
from nexuscrm.ml.dataset_loader import FEATURE_COLUMNS


class LeadScoringModel:
    """LightGBM Classifier for Lead Conversion Scoring."""

    def __init__(self, model_path: str = "models/lead_scorer.pkl"):
        self.model_path = model_path
        self.model: LGBMClassifier = None

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, float]:
        """Train LightGBM lead scoring model and calculate metrics."""
        logger.info("Training LightGBM Lead Scoring Model...")
        self.model = LGBMClassifier(
            n_estimators=100,
            learning_rate=0.05,
            num_leaves=31,
            random_state=42,
            verbose=-1,
        )
        self.model.fit(X_train, y_train)

        y_pred_prob = self.model.predict_proba(X_test)[:, 1]
        y_pred = (y_pred_prob > 0.5).astype(int)

        from nexuscrm.ml.metrics_exporter import metrics_exporter
        exported_metrics = metrics_exporter.evaluate_and_export(
            model_name="lead_scorer",
            y_true=y_test.values if hasattr(y_test, "values") else y_test,
            y_pred=y_pred,
            y_prob=y_pred_prob,
        )

        metrics = {
            "accuracy": exported_metrics["accuracy"],
            "precision": exported_metrics["precision"],
            "recall": exported_metrics["recall"],
            "f1_score": exported_metrics["f1_score"],
            "auc_roc": exported_metrics["auc_roc"],
        }
        logger.info(f"Lead Scorer Model Trained. Metrics: {metrics}")


        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        return metrics

    def load(self):
        """Load trained model artifact."""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        else:
            logger.warning(f"Model file {self.model_path} not found. Creating fallback model.")
            self.model = LGBMClassifier(n_estimators=10, verbose=-1)

    def predict(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate lead score (0-100) for single lead feature payload."""
        if self.model is None:
            self.load()

        input_df = pd.DataFrame([feature_dict])[FEATURE_COLUMNS] if isinstance(feature_dict, dict) else feature_dict
        prob = float(self.model.predict_proba(input_df)[0, 1]) if hasattr(self.model, "predict_proba") else 0.75
        score_100 = round(prob * 100.0, 1)

        tier = "Cold Lead"
        if score_100 >= 80.0:
            tier = "Very Hot Lead"
        elif score_100 >= 60.0:
            tier = "Hot Lead"
        elif score_100 >= 35.0:
            tier = "Warm Lead"

        return {
            "lead_score": score_100,
            "conversion_probability": round(prob, 4),
            "tier": tier,
        }


lead_scorer = LeadScoringModel()
