from pathlib import Path
from datetime import datetime, timedelta
import random
import uuid

import pandas as pd
from faker import Faker


fake = Faker()

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "synthetic"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CUSTOMER_COUNT = 100
TRANSACTION_COUNT = 500
CASE_COUNT = 50

COUNTRIES_AND_CITIES = {
    "Ireland": ["Dublin", "Cork", "Galway", "Limerick", "Waterford"],
    "United Kingdom": ["London", "Manchester", "Birmingham", "Leeds", "Bristol"],
    "India": ["Mumbai", "Pune", "Bengaluru", "Hyderabad", "Delhi"],
    "Germany": ["Berlin", "Munich", "Frankfurt", "Hamburg", "Cologne"],
    "France": ["Paris", "Lyon", "Marseille", "Nice", "Toulouse"],
}

CUSTOMER_SEGMENTS = ["STUDENT", "RETAIL", "SME", "PREMIUM", "HIGH_NET_WORTH"]
KYC_STATUSES = ["VERIFIED", "PENDING", "FAILED", "EXPIRED"]
RISK_RATINGS = ["LOW", "MEDIUM", "HIGH"]

CURRENCIES = ["EUR", "GBP", "USD", "INR"]
MERCHANT_CATEGORIES = [
    "GROCERIES",
    "TRAVEL",
    "GAMING",
    "CRYPTO",
    "ELECTRONICS",
    "SUBSCRIPTION",
    "FOOD_DELIVERY",
    "CASH_WITHDRAWAL",
    "ONLINE_MARKETPLACE",
    "UNKNOWN",
]
CHANNELS = ["CARD", "BANK_TRANSFER", "MOBILE_APP", "WEB", "ATM", "POS"]
TRANSACTION_STATUSES = ["SUCCESS", "FAILED", "PENDING", "REVERSED"]

CASE_TYPES = [
    "SUSPICIOUS_TRANSACTION",
    "CHARGEBACK_DISPUTE",
    "KYC_DOCUMENT_REVIEW",
    "AML_ESCALATION",
    "FAILED_PAYMENT_INVESTIGATION",
    "CUSTOMER_COMPLAINT",
    "LOAN_AFFORDABILITY_REVIEW",
    "ACCOUNT_TAKEOVER_RISK",
]
PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
CASE_STATES = ["OPEN", "IN_REVIEW", "WAITING_FOR_CUSTOMER", "ESCALATED", "RESOLVED"]
SOURCE_CHANNELS = ["SYSTEM", "CUSTOMER_SUPPORT", "MOBILE_APP", "WEB_PORTAL", "BACK_OFFICE"]


def random_datetime_within_days(days_back: int) -> datetime:
    return datetime.utcnow() - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


def generate_customers() -> pd.DataFrame:
    rows = []

    for _ in range(CUSTOMER_COUNT):
        country = random.choice(list(COUNTRIES_AND_CITIES.keys()))
        city = random.choice(COUNTRIES_AND_CITIES[country])
        account_open_date = random_datetime_within_days(1500).date()

        rows.append(
            {
                "customer_id": str(uuid.uuid4()),
                "full_name": fake.name(),
                "email": fake.unique.email(),
                "phone_number": fake.phone_number(),
                "country": country,
                "city": city,
                "account_open_date": account_open_date.isoformat(),
                "customer_segment": random.choice(CUSTOMER_SEGMENTS),
                "kyc_status": random.choices(
                    KYC_STATUSES,
                    weights=[70, 15, 7, 8],
                    k=1,
                )[0],
                "risk_rating": random.choices(
                    RISK_RATINGS,
                    weights=[65, 25, 10],
                    k=1,
                )[0],
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    return pd.DataFrame(rows)


def generate_transactions(customers_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    customer_ids = customers_df["customer_id"].tolist()

    for _ in range(TRANSACTION_COUNT):
        customer_id = random.choice(customer_ids)
        merchant_category = random.choice(MERCHANT_CATEGORIES)

        amount = round(random.uniform(5, 1200), 2)

        if merchant_category in ["CRYPTO", "TRAVEL", "ELECTRONICS"]:
            amount = round(random.uniform(250, 5000), 2)

        is_suspicious = (
            merchant_category in ["CRYPTO", "UNKNOWN", "GAMING"]
            and amount > 750
        ) or random.random() < 0.08

        rows.append(
            {
                "transaction_id": str(uuid.uuid4()),
                "customer_id": customer_id,
                "transaction_date": random_datetime_within_days(365).isoformat(),
                "amount": amount,
                "currency": random.choice(CURRENCIES),
                "merchant_name": fake.company(),
                "merchant_category": merchant_category,
                "channel": random.choice(CHANNELS),
                "device_id": f"DEV-{uuid.uuid4().hex[:10].upper()}",
                "location": fake.city(),
                "transaction_status": random.choices(
                    TRANSACTION_STATUSES,
                    weights=[82, 8, 6, 4],
                    k=1,
                )[0],
                "is_suspicious": is_suspicious,
                "created_at": datetime.utcnow().isoformat(),
            }
        )

    return pd.DataFrame(rows)


def build_case_description(case_type: str) -> str:
    descriptions = {
        "SUSPICIOUS_TRANSACTION": "Transaction flagged due to unusual spending pattern or high-risk merchant activity.",
        "CHARGEBACK_DISPUTE": "Customer disputed a transaction and requested investigation for possible chargeback.",
        "KYC_DOCUMENT_REVIEW": "Customer KYC status requires manual document review before account restrictions are removed.",
        "AML_ESCALATION": "Transaction behaviour matched AML risk indicators and requires compliance review.",
        "FAILED_PAYMENT_INVESTIGATION": "Payment failed or reversed and requires operational investigation.",
        "CUSTOMER_COMPLAINT": "Customer raised a complaint requiring service review and response within SLA.",
        "LOAN_AFFORDABILITY_REVIEW": "Customer affordability requires review based on account behaviour and risk signals.",
        "ACCOUNT_TAKEOVER_RISK": "Account activity indicates possible takeover risk due to device or location anomaly.",
    }
    return descriptions[case_type]


def generate_cases(customers_df: pd.DataFrame, transactions_df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for _ in range(CASE_COUNT):
        transaction = transactions_df.sample(1).iloc[0]
        case_type = random.choice(CASE_TYPES)

        if bool(transaction["is_suspicious"]):
            case_type = random.choice(
                ["SUSPICIOUS_TRANSACTION", "AML_ESCALATION", "ACCOUNT_TAKEOVER_RISK"]
            )

        priority = random.choices(
            PRIORITIES,
            weights=[30, 40, 22, 8],
            k=1,
        )[0]

        rows.append(
            {
                "case_id": str(uuid.uuid4()),
                "customer_id": transaction["customer_id"],
                "transaction_id": transaction["transaction_id"],
                "case_type": case_type,
                "description": build_case_description(case_type),
                "priority": priority,
                "state": random.choice(CASE_STATES),
                "source_channel": random.choice(SOURCE_CHANNELS),
                "created_at": random_datetime_within_days(120).isoformat(),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    customers_df = generate_customers()
    transactions_df = generate_transactions(customers_df)
    cases_df = generate_cases(customers_df, transactions_df)

    customers_path = OUTPUT_DIR / "customers.csv"
    transactions_path = OUTPUT_DIR / "transactions.csv"
    cases_path = OUTPUT_DIR / "cases.csv"

    customers_df.to_csv(customers_path, index=False)
    transactions_df.to_csv(transactions_path, index=False)
    cases_df.to_csv(cases_path, index=False)

    print("Synthetic data generated successfully.")
    print(f"Customers: {len(customers_df)} rows -> {customers_path}")
    print(f"Transactions: {len(transactions_df)} rows -> {transactions_path}")
    print(f"Cases: {len(cases_df)} rows -> {cases_path}")


if __name__ == "__main__":
    main()