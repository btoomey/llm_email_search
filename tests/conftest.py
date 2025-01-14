import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from llm_email_search.extract_emails_to_sqlite import Base, Email

MOCK_EMAIL = {
    "id": "12345",
    "internalDate": "1647123456789",
    "payload": {
        "headers": [
            {"name": "From", "value": "sender@example.com"},
            {"name": "Subject", "value": "Test Subject"},
        ],
        "body": {
            "data": "VGhpcyBpcyBhIHRlc3QgZW1haWw="  # "This is a test email" in base64
        },
        "parts": [
            {
                "mimeType": "text/plain",
                "filename": "test.txt",
                "body": {"data": "VGhpcyBpcyBhIHRlc3QgZW1haWw="},
            }
        ],
    },
}


@pytest.fixture
def temp_db_path(tmp_path):
    """Provides a temporary database path."""
    return str(tmp_path / "test.db")


@pytest.fixture
def temp_embeddings_path(tmp_path):
    """Provides a temporary embeddings database path."""
    return str(tmp_path / "test_embeddings.db")


@pytest.fixture
def mock_gmail_message():
    """Returns a mock Gmail message structure."""
    return MOCK_EMAIL


@pytest.fixture
def sample_db_with_emails(temp_db_path):
    """Creates a test database with sample emails."""
    engine = create_engine(f"sqlite:///{temp_db_path}")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Add sample emails
    sample_emails = [
        Email(
            sender="test1@example.com",
            subject="Test Email 1",
            body="This is test email 1",
            timestamp=1647123456789,
            attachment_types=".pdf,.txt",
        ),
        Email(
            sender="test2@example.com",
            subject="Test Email 2",
            body="This is test email 2",
            timestamp=1647123456790,
            attachment_types=".jpg",
        ),
    ]

    session.add_all(sample_emails)
    session.commit()
    session.close()

    return temp_db_path
