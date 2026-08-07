"""Enterprise CRM Dataset Loader and Preprocessor."""

import os
import pandas as pd
from typing import Tuple
from sklearn.model_selection import train_test_split

FEATURE_COLUMNS = [
    "days_since_last_contact",
    "activity_count_30d",
    "activity_count_90d",
    "avg_sentiment_30d",
    "email_response_rate",
    "open_support_tickets",
    "deal_count",
    "deal_win_rate",
    "avg_deal_value",
    "days_as_customer",
    "contract_months_remaining",
    "monthly_recurring_revenue",
    "net_promoter_score",
]


from nexuscrm.ml.data_cleaner import data_cleaner


def load_crm_dataset(csv_path: str = "data/enterprise_crm_dataset.csv") -> pd.DataFrame:
    """Load and clean enterprise CRM dataset from CSV."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file {csv_path} not found. Run scripts/generate_ml_dataset.py first.")
    raw_df = pd.read_csv(csv_path)
    clean_df, summary = data_cleaner.clean_dataset(raw_df)
    return clean_df



def prepare_churn_data(csv_path: str = "data/enterprise_crm_dataset.csv") -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Prepare train/test splits for Churn Risk Model."""
    df = load_crm_dataset(csv_path)
    X = df[FEATURE_COLUMNS]
    y = df["churn_label"]
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def prepare_lead_scoring_data(csv_path: str = "data/enterprise_crm_dataset.csv") -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Prepare train/test splits for Lead Scoring Model."""
    df = load_crm_dataset(csv_path)
    X = df[FEATURE_COLUMNS]
    y = df["lead_converted_label"]
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
