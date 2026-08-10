"""Senior Indian Enterprise CRM Data Generator.

Generates 1,500 realistic Indian enterprise customer profile records with multi-dimensional
behavioral features and historical revenue time-series data for production ML training.
"""

import os
import numpy as np
import pandas as pd
from faker import Faker

fake = Faker('en_IN')
np.random.seed(42)

NUM_CUSTOMERS = 1500

INDIAN_COMPANIES_POOL = [
    "Infosys Limited", "TCS", "Wipro Technologies", "HCLTech", "Tech Mahindra",
    "Reliance Industries", "Jio Platforms", "Razorpay Software", "Zerodha Broking",
    "Zomato Limited", "Swiggy", "Freshworks India", "Zoho Corporation", "Postman",
    "Paytm", "PhonePe", "CRED", "Flipkart Enterprise", "Meesho", "InMobi Tech",
    "Nykaa Retail", "OYO Rooms", "Ola Electric", "Delhivery Logistics", "Pine Labs",
    "Policybazaar", "Info Edge", "Persistent Systems", "Coforge", "Mphasis",
    "LTTS", "Cyient", "Titan Company", "Tata Motors", "HDFC Bank", "ICICI Bank",
    "Axis Bank", "Bharti Airtel", "Sun Pharma", "Dr. Reddy's Lab", "Cipla",
    "Biocon", "Mahindra & Mahindra", "Bajaj Finserv", "Larsen & Toubro", "Adani Enterprises",
]


def generate_crm_dataset():
    """Generate senior enterprise Indian CRM customer dataset."""
    print(f"Generating {NUM_CUSTOMERS} realistic Indian enterprise CRM customer records...")

    industries = ["IT Services & Consulting", "Fintech & Payments", "SaaS Software", "E-Commerce", "Banking & Finance", "Healthcare & Pharma", "Telecom & Digital"]
    data = []

    for i in range(NUM_CUSTOMERS):
        customer_id = f"CUST-IN-{i+10001}"
        base_comp = np.random.choice(INDIAN_COMPANIES_POOL)
        company_name = f"{base_comp} (Unit {fake.city()})"
        industry = np.random.choice(industries)

        # Behavioral & Engagement features
        days_since_last_contact = int(np.random.gamma(shape=3.0, scale=12.0))
        days_since_last_contact = min(180, max(1, days_since_last_contact))

        activity_count_30d = max(0, int(np.random.poisson(lam=4.0)))
        activity_count_90d = activity_count_30d + max(0, int(np.random.poisson(lam=9.0)))

        avg_sentiment_30d = round(float(np.random.normal(loc=0.2, scale=0.4)), 2)
        avg_sentiment_30d = min(1.0, max(-1.0, avg_sentiment_30d))

        email_response_rate = round(float(np.random.beta(a=5, b=3)), 2)
        open_support_tickets = int(np.random.poisson(lam=0.8))

        deal_count = max(1, int(np.random.poisson(lam=3.0)))
        deal_win_rate = round(float(np.random.beta(a=4, b=4)), 2)
        avg_deal_value = round(float(np.random.lognormal(mean=10.8, sigma=0.8)), 2)

        days_as_customer = int(np.random.uniform(30, 1460))
        contract_months_remaining = int(np.random.uniform(0, 24))
        monthly_recurring_revenue = round(float(np.random.lognormal(mean=8.5, sigma=0.6)), 2)
        net_promoter_score = int(min(10, max(1, np.random.normal(loc=7.2, scale=2.0))))

        # Domain Logic Target Calculation: Churn Risk Score
        churn_logits = (
            (days_since_last_contact / 40.0) * 1.5
            + (open_support_tickets * 0.8)
            - (avg_sentiment_30d * 2.0)
            - (email_response_rate * 1.5)
            + (1.0 if contract_months_remaining <= 2 else -0.5)
            - (net_promoter_score * 0.3)
            + np.random.normal(0, 0.5)
        )
        churn_prob = 1.0 / (1.0 + np.exp(-churn_logits))
        churn_label = 1 if churn_prob > 0.55 else 0

        # Domain Logic Target Calculation: Lead Conversion
        lead_logits = (
            (activity_count_30d * 0.15)
            + (avg_sentiment_30d * 1.2)
            + (deal_win_rate * 1.5)
            + (net_promoter_score * 0.15)
            - (days_since_last_contact * 0.08)
            - 1.8
            + np.random.normal(0, 0.4)
        )
        lead_prob = 1.0 / (1.0 + np.exp(-lead_logits))
        lead_converted_label = 1 if lead_prob > 0.50 else 0

        data.append({
            "customer_id": customer_id,
            "company_name": company_name,
            "industry": industry,
            "days_since_last_contact": days_since_last_contact,
            "activity_count_30d": activity_count_30d,
            "activity_count_90d": activity_count_90d,
            "avg_sentiment_30d": avg_sentiment_30d,
            "email_response_rate": email_response_rate,
            "open_support_tickets": open_support_tickets,
            "deal_count": deal_count,
            "deal_win_rate": deal_win_rate,
            "avg_deal_value": avg_deal_value,
            "days_as_customer": days_as_customer,
            "contract_months_remaining": contract_months_remaining,
            "monthly_recurring_revenue": monthly_recurring_revenue,
            "net_promoter_score": net_promoter_score,
            "churn_label": churn_label,
            "lead_converted_label": lead_converted_label,
        })

    df = pd.DataFrame(data)
    os.makedirs("data", exist_ok=True)
    csv_path = "data/enterprise_crm_dataset.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved Indian enterprise CRM dataset ({len(df)} rows) to {csv_path}.")
    print(f"Churn rate: {df['churn_label'].mean():.2%}, Conversion rate: {df['lead_converted_label'].mean():.2%}")

    # Generate 24-Month Monthly Revenue Time Series Data
    date_range = pd.date_range(start="2024-01-01", periods=24, freq="MS")
    base_revenue = 250000.0
    revenue_data = []
    for idx, dt in enumerate(date_range):
        trend = idx * 8500.0
        seasonality = 35000.0 * np.sin(idx * np.pi / 6)  # 12-month seasonality
        noise = np.random.normal(0, 12000.0)
        revenue = round(base_revenue + trend + seasonality + noise, 2)
        revenue_data.append({"ds": dt.strftime("%Y-%m-%d"), "y": revenue})

    df_rev = pd.DataFrame(revenue_data)
    rev_path = "data/historical_monthly_revenue.csv"
    df_rev.to_csv(rev_path, index=False)
    print(f"Saved 24-month revenue time-series ({len(df_rev)} months) to {rev_path}.")


if __name__ == "__main__":
    generate_crm_dataset()
