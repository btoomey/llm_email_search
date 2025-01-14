from llm_email_search.extract_emails_to_sqlite import (
    get_header,
    extract_message_body,
    extract_attachment_types,
)

def test_get_header():
    headers = [
        {"name": "From", "value": "sender@example.com"},
        {"name": "Subject", "value": "Test Subject"},
    ]
    assert get_header(headers, "From") == "sender@example.com"
    assert get_header(headers, "Subject") == "Test Subject"
    assert get_header(headers, "NonExistent") is None


def test_extract_message_body(mock_gmail_message):
    body = extract_message_body(mock_gmail_message["payload"])
    assert body == "This is a test email"


def test_extract_attachment_types():
    parts = [
        {"filename": "document.pdf"},
        {"filename": "image.jpg"},
        {"filename": "noextension"},
    ]
    types = extract_attachment_types(parts)
    assert ".pdf,.jpg,unknown" == types


# TODO: Add test for extract_message_data

# TODO: Add test for extract_emails
# Even with MagicMock, this is a bit tricky to test
# because it interacts with the Gmail API while having
# a SQLAlchemy session open to ensure uniqueness of the database