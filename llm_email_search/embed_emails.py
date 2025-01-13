import argparse
import os
import chromadb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from extract_emails_to_sqlite import Email
from chromadb.utils import embedding_functions


def main():
    parser = argparse.ArgumentParser(description="Embed emails into vector database")
    parser.add_argument(
        "--sql-path",
        type=str,
        default="emails.db",
        help="SQLite database file path (default: emails.db)",
    )
    parser.add_argument(
        "--embeddings-path",
        type=str,
        default="embedded_emails.db",
        help="Path to store embeddings database (default: embedded_emails.db)",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Name of sentence transformer model (default: sentence-transformers/all-MiniLM-L6-v2)",
    )
    args = parser.parse_args()
    if not os.path.exists(args.sql_path):
        raise FileNotFoundError(f"SQLite database file not found at {args.sql_path}")

    engine = create_engine(f"sqlite:///{args.sql_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    client = chromadb.PersistentClient(path=args.embeddings_path)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=args.model_name
    )
    collection = client.get_or_create_collection(
        "test_emails", embedding_function=sentence_transformer_ef
    )

    documents = []
    metadatas = []
    ids = []
    for email in session.query(Email).all():
        documents.append(email.body)
        metadatas.append(
            {
                "sender": email.sender,
                "subject": email.subject,
                "timestamp": str(
                    email.timestamp
                ),  # TO-DO: Decide whether we just want to go back to epoch time for everything
                # Chroma doesn't support datetime objects, so we need to convert to string for now
                "attachment_types": email.attachment_types,
            }
        )
        ids.append(str(email.id))

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )


if __name__ == "__main__":
    main()
