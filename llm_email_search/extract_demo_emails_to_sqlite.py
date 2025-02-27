import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pandas as pd

from llm_email_search.extract_emails_to_sqlite import Email, Base
from llm_email_search.logger import setup_logger

logger = setup_logger(__name__)

# Demo is based on the csv here:
# https://www.kaggle.com/datasets/subhajournal/phishingemails

def extract_demo_emails_to_sqlite(database: str = "demo_emails.db") -> None:
    engine = create_engine(f"sqlite:///{database}")
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)

    # Read the CSV file
    df = pd.read_csv("data/Phishing_email.csv").drop_duplicates(subset=["Email Text"])
    all_emails = []
    for row in df["Email Text"]:
        if row is None or row == "" or pd.isna(row):
            continue
        email = Email(
            sender=None,
            subject=None,
            body=row,
            timestamp=None,
            attachment_types=None,
        )
        all_emails.append(email)
    session.add_all(all_emails)
    logger.info(f"Added {len(all_emails)} emails to the database")
    session.commit()
    session.close()


def main():
    parser = argparse.ArgumentParser(description="Extract public emails to SQLite database")
    parser.add_argument("--database", type=str, default="demo_emails.db", help="Path to SQLite database file")
    args = parser.parse_args()
    extract_demo_emails_to_sqlite(args.database)

if __name__ == "__main__":
    main()
