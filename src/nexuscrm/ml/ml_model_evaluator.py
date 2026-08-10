"""ML Model Evaluator and Best-Model Selector.

Trains and compares 5 classification algorithms side-by-side:
  1. XGBoost Classifier
  2. LightGBM Classifier
  3. Random Forest Classifier
  4. Gradient Boosting Classifier
  5. Extra Trees Classifier

Picks the best-performing model by AUC-ROC + F1, saves it, and
exports a comparison report so you can see exactly why it won.
"""

import os
import joblib
import pandas as pd
from typing import Dict, Any

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

from nexuscrm.core.logging import logger
from nexuscrm.ml.dataset_loader import prepare_churn_data, prepare_lead_scoring_data
from nexuscrm.ml.metrics_exporter import metrics_exporter


class ModelEvaluator:
    """Trains multiple classifiers, compares their metrics, and deploys the best one."""

    def __init__(self):
        self.candidates = {
            "xgboost": XGBClassifier(
                n_estimators=100, max_depth=5, learning_rate=0.05,
                eval_metric="logloss", random_state=42,
            ),
            "lightgbm": LGBMClassifier(
                n_estimators=100, max_depth=5, learning_rate=0.05,
                verbose=-1, random_state=42,
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42,
            ),
            "extra_trees": ExtraTreesClassifier(
                n_estimators=100, max_depth=10, random_state=42,
            ),
        }

    def run(self, task_name: str, prepare_fn) -> Dict[str, Any]:
        """Train all candidates on task data, pick the winner, and save it."""
        logger.info(f"Starting model evaluation for task: [{task_name}]")
        X_train, X_test, y_train, y_test = prepare_fn()

        results = []
        trained = {}

        for name, clf in self.candidates.items():
            logger.info(f"  Training [{name}]...")
            clf.fit(X_train, y_train)

            y_prob = clf.predict_proba(X_test)[:, 1]
            y_pred = (y_prob > 0.5).astype(int)

            results.append({
                "task": task_name,
                "model": name,
                "accuracy":  round(float(accuracy_score(y_test, y_pred)), 4),
                "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
                "recall":    round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
                "f1_score":  round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
                "auc_roc":   round(float(roc_auc_score(y_test, y_prob)), 4),
            })
            trained[name] = (clf, results[-1]["auc_roc"])

        # Sort by AUC-ROC descending — highest score wins
        results.sort(key=lambda r: r["auc_roc"], reverse=True)
        best_name = results[0]["model"]
        best_clf, best_auc = trained[best_name]

        logger.info(
            f"Best model for [{task_name}]: {best_name.upper()} "
            f"(AUC-ROC={best_auc:.4f})"
        )

        # Save the winning model
        os.makedirs("models", exist_ok=True)
        save_path = os.path.join("models", f"best_{task_name}_model.pkl")
        joblib.dump(best_clf, save_path)

        # Write comparison reports
        self._save_comparison_report(task_name, results, best_name)

        return {
            "best_model": best_name,
            "best_auc":   best_auc,
            "model_path": save_path,
            "results":    results,
        }

    def _save_comparison_report(self, task_name: str, results: list, best_name: str):
        """Write a CSV and a Markdown comparison table to models/."""
        df = pd.DataFrame(results)
        csv_path = os.path.join("models", f"{task_name}_model_comparison.csv")
        df.to_csv(csv_path, index=False)

        md_path = os.path.join("models", f"{task_name}_model_comparison.md")
        with open(md_path, "w") as f:
            f.write(f"# Model Comparison Report — {task_name.upper()}\n\n")
            f.write(f"**Deployed Model**: `{best_name.upper()}` (highest AUC-ROC)\n\n")
            f.write("| Rank | Model | Accuracy | Precision | Recall | F1 | AUC-ROC |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for i, row in enumerate(results):
                tag = "**BEST**" if i == 0 else f"#{i + 1}"
                f.write(
                    f"| {tag} | {row['model'].upper()} "
                    f"| {row['accuracy']:.4f} | {row['precision']:.4f} "
                    f"| {row['recall']:.4f} | {row['f1_score']:.4f} "
                    f"| {row['auc_roc']:.4f} |\n"
                )

        logger.info(f"Saved model comparison report to {csv_path} and {md_path}.")


model_evaluator = ModelEvaluator()
