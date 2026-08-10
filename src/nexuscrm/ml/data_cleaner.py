"""Data cleaning and preprocessing pipeline."""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

from nexuscrm.core.logging import logger
from nexuscrm.ml.dataset_loader import FEATURE_COLUMNS


class DataCleaner:
    """Data cleaning, outlier handling, and imputation pipeline."""

    def __init__(self):
        self.stats_summary: Dict[str, Any] = {}

    def clean_dataset(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Perform comprehensive data cleaning and validation pipeline."""
        logger.info(f"Starting senior ML data cleaning pipeline on {len(df)} records...")
        initial_rows = len(df)

        # 1. Deduplication
        df = df.drop_duplicates().copy()
        dedup_count = initial_rows - len(df)

        # 2. Null Value Imputation
        null_counts = df[FEATURE_COLUMNS].isnull().sum().to_dict()
        for col in FEATURE_COLUMNS:
            if df[col].isnull().sum() > 0:
                if df[col].dtype in [np.float64, np.int64]:
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                else:
                    mode_val = df[col].mode()[0]
                    df[col] = df[col].fillna(mode_val)

        # 3. Outlier Clipping (IQR Capping for continuous variables)
        clipped_cols = 0
        for col in ["avg_deal_value", "monthly_recurring_revenue", "days_since_last_contact"]:
            if col in df.columns:
                q1 = df[col].quantile(0.01)
                q3 = df[col].quantile(0.99)
                iqr = q3 - q1
                upper_bound = q3 + 1.5 * iqr
                lower_bound = max(0, q1 - 1.5 * iqr)
                df[col] = np.clip(df[col], lower_bound, upper_bound)
                clipped_cols += 1

        # 4. Invariant Validation (e.g. non-negative constraints)
        for col in ["days_since_last_contact", "activity_count_30d", "activity_count_90d", "open_support_tickets"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: max(0, x))

        # 5. Sentiment Normalization (-1.0 to +1.0)
        if "avg_sentiment_30d" in df.columns:
            df["avg_sentiment_30d"] = df["avg_sentiment_30d"].apply(lambda x: min(1.0, max(-1.0, x)))

        cleaning_summary = {
            "initial_rows": initial_rows,
            "cleaned_rows": len(df),
            "duplicates_removed": dedup_count,
            "null_imputations": sum(null_counts.values()),
            "outliers_clipped_cols": clipped_cols,
            "status": "fully_clean",
        }

        logger.info(f"Data cleaning complete: {cleaning_summary}")
        self.stats_summary = cleaning_summary
        return df, cleaning_summary


data_cleaner = DataCleaner()
SeniorDataCleaner = DataCleaner
