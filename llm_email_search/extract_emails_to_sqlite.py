import base64
import os
import pickle
from datetime import UTC, datetime
import argparse

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

parser = argparse.ArgumentParser(description="Download emails to SQLite database")
parser.add_argument(
    "--database",
    type=str,
    default="emails.db",
    help="SQLite database file path (default: emails.db)",
)
parser.add_argument(
    "--max-emails",
    type=int,
    default=1000,
    help="Maximum number of emails to download (default: 1000)",
)
args = parser.parse_args()

Base = declarative_base()
engine = create_engine(f"sqlite:///{args.database}")
Session = sessionmaker(bind=engine)
session = Session()


class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True)
    sender = Column(String, nullable=False)
    subject = Column(String)
    body = Column(String)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(UTC))
    attachment_types = Column(String)  # Comma-separated list of attachment types


Base.metadata.create_all(engine)


def get_header(headers, name):
    """Helper function to extract a specific header."""
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]
    return None


def extract_message_body(payload):
    """Extract the text body of the email."""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain" and "body" in part:
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
            elif part["mimeType"] == "text/html" and "body" in part:
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
    elif "body" in payload and "data" in payload["body"]:
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
    return "No body text found."


def extract_attachment_types(parts):
    """Extract the file types of attachments from the email parts."""
    attachment_types = []
    for part in parts:
        if part.get("filename"):  # If there is a filename, it's an attachment
            filename = part["filename"]
            # Extract the file type (extension)
            file_extension = os.path.splitext(filename)[
                1
            ]  # Get the extension (e.g., .pdf)
            attachment_types.append(file_extension if file_extension else "unknown")
    return ",".join(attachment_types) if attachment_types else ""


def extract_message_data(service, message_id):
    """Extract sender, subject, body text, and attachment types from an email."""
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    payload = msg["payload"]
    headers = payload.get("headers", [])

    # Extract sender and subject
    sender = get_header(headers, "From")
    subject = get_header(headers, "Subject")

    # Extract email body
    body_text = extract_message_body(payload)

    # Check for attachments and extract file types
    attachment_types = ""
    if "parts" in payload:
        attachment_types = extract_attachment_types(payload["parts"])

    # Extract timestamp from internalDate (milliseconds since epoch)
    timestamp = datetime.fromtimestamp(int(msg["internalDate"]) / 1000, UTC)

    return {
        "sender": sender,
        "subject": subject,
        "body": body_text,
        "attachment_types": attachment_types,
        "timestamp": timestamp,
    }


def authenticate():
    """Authenticate with Gmail API and return credentials."""
    creds = None
    # Load previously saved credentials
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials, request new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def main():
    creds = authenticate()

    # Build the Gmail service
    service = build("gmail", "v1", credentials=creds)

    # Fetch messages
    results = (
        service.users()
        .messages()
        .list(userId="me", maxResults=args.max_emails)
        .execute()
    )
    messages = results.get("messages", [])
    all_emails = []
    for message in messages:
        message_data = extract_message_data(service, message["id"])
        # Check if email with the same timestamp, sender, subject, body, and attachment types already exists
        existing_email = (
            session.query(Email)
            .filter(
                Email.timestamp == message_data["timestamp"],
                Email.sender == message_data["sender"],
                Email.subject == message_data["subject"],
                Email.body == message_data["body"],
                Email.attachment_types == message_data["attachment_types"],
            )
            .first()
        )
        if not existing_email:
            all_emails.append(Email(**message_data))

    if all_emails:
        session.add_all(all_emails)
        session.commit()

    
    session.close()

if __name__ == "__main__":
    main()
