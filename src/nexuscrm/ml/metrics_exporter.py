"""Automated ML Model Performance Metrics Exporter."""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)

from nexuscrm.core.logging import logger


class MetricsExporter:
    """Calculates, formats, and auto-saves comprehensive model evaluation metrics."""

    @staticmethod
    def evaluate_and_export(
        model_name: str,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
        output_dir: str = "models",
    ) -> Dict[str, Any]:
        """Compute full classification metrics and persist to JSON, CSV, and Markdown files."""
        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        auc = float(roc_auc_score(y_true, y_prob)) if y_prob is not None else 0.0

        cm = confusion_matrix(y_true, y_pred).tolist()
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        metrics_dict = {
            "model_name": model_name,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "auc_roc": round(auc, 4),
            "confusion_matrix": {
                "true_negatives": int(tn),
                "false_positives": int(fp),
                "false_negatives": int(fn),
                "true_positives": int(tp),
                "matrix": cm,
            },
            "classification_report": classification_report(y_true, y_pred, output_dict=True),
        }

        os.makedirs(output_dir, exist_ok=True)

        # 1. Save JSON Metrics
        json_path = os.path.join(output_dir, f"{model_name}_metrics.json")
        with open(json_path, "w") as f:
            json.dump(metrics_dict, f, indent=2)

        # 2. Append to Master Summary CSV
        summary_csv = os.path.join(output_dir, "all_model_metrics.csv")
        row_df = pd.DataFrame([{
            "model_name": model_name,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "auc_roc": round(auc, 4),
            "true_positives": int(tp),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
        }])

        if os.path.exists(summary_csv):
            existing_df = pd.read_csv(summary_csv)
            existing_df = existing_df[existing_df["model_name"] != model_name]
            updated_df = pd.concat([existing_df, row_df], ignore_index=True)
            updated_df.to_csv(summary_csv, index=False)
        else:
            row_df.to_csv(summary_csv, index=False)

        # 3. Save Human-Readable Markdown Report
        md_path = os.path.join(output_dir, f"{model_name}_metrics_report.md")
        with open(md_path, "w") as f:
            f.write(f"# Performance Report: {model_name}\n\n")
            f.write(f"- **Accuracy**: `{acc:.4f}`\n")
            f.write(f"- **Precision**: `{prec:.4f}`\n")
            f.write(f"- **Recall**: `{rec:.4f}`\n")
            f.write(f"- **F1 Score**: `{f1:.4f}`\n")
            f.write(f"- **AUC-ROC**: `{auc:.4f}`\n\n")
            f.write("## Confusion Matrix\n")
            f.write(f"| Actual / Predicted | Negative | Positive |\n")
            f.write(f"|---|---|---|\n")
            f.write(f"| **Negative** | {tn} (TN) | {fp} (FP) |\n")
            f.write(f"| **Positive** | {fn} (FN) | {tp} (TP) |\n")

        logger.info(f"Saved evaluation metrics for {model_name} to {json_path}, {summary_csv}, and {md_path}.")
        return metrics_dict


metrics_exporter = MetricsExporter()
