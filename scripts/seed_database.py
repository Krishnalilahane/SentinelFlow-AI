from pathlib import Path
from datetime import datetime
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

import pandas as pd
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.db.models import Customer, Transaction


SYNTHETIC_DIR = BASE_DIR / "data" / "synthetic"

CUSTOMERS_CSV = SYNTHETIC_DIR / "customers.csv"
TRANSACTIONS_CSV = SYNTHETIC_DIR / "transactions.csv"


def parse_datetime(value: str) -> datetime:
    if pd.isna(value):
        return datetime.utcnow()

    return pd.to_datetime(value).to_pydatetime()


def seed_customers(db, customers_df: pd.DataFrame) -> int:
    inserted_count = 0

    for _, row in customers_df.iterrows():
        customer_id = str(row["customer_id"])

        existing_customer = db.get(Customer, customer_id)
        if existing_customer:
            continue

        customer = Customer(
            id=customer_id,
            name=row.get("full_name"),
            email=row.get("email"),
            created_at=parse_datetime(row.get("created_at")),
        )

        db.add(customer)
        inserted_count += 1

    return inserted_count


def seed_transactions(db, transactions_df: pd.DataFrame) -> int:
    inserted_count = 0

    for _, row in transactions_df.iterrows():
        transaction_id = str(row["transaction_id"])
        customer_id = str(row["customer_id"])

        existing_transaction = db.get(Transaction, transaction_id)
        if existing_transaction:
            continue

        existing_customer = db.get(Customer, customer_id)
        if not existing_customer:
            continue

        transaction = Transaction(
            id=transaction_id,
            customer_id=customer_id,
            amount=str(row.get("amount")),
            currency=row.get("currency"),
            created_at=parse_datetime(row.get("created_at")),
        )

        db.add(transaction)
        inserted_count += 1

    return inserted_count


def main() -> None:
    if not CUSTOMERS_CSV.exists():
        raise FileNotFoundError(f"Missing file: {CUSTOMERS_CSV}")

    if not TRANSACTIONS_CSV.exists():
        raise FileNotFoundError(f"Missing file: {TRANSACTIONS_CSV}")

    customers_df = pd.read_csv(CUSTOMERS_CSV)
    transactions_df = pd.read_csv(TRANSACTIONS_CSV)

    db = SessionLocal()

    try:
        inserted_customers = seed_customers(db, customers_df)

        # Important:
        # On a fresh database, customers are added to the current session first.
        # Flushing makes them visible before transaction seeding checks foreign keys.
        db.flush()

        inserted_transactions = seed_transactions(db, transactions_df)

        db.commit()

        print("Database seeding completed successfully.")
        print(f"Customers inserted: {inserted_customers}")
        print(f"Transactions inserted: {inserted_transactions}")
        print(
            "Cases were not seeded because Stage 1 case schema is intentionally "
            "narrower than Stage 2 synthetic case data."
        )

    except IntegrityError as error:
        db.rollback()
        print("Database seeding failed due to an integrity error.")
        print(str(error))
        raise

    except Exception as error:
        db.rollback()
        print("Database seeding failed.")
        print(str(error))
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()