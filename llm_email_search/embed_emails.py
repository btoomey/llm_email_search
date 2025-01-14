import argparse
import os
import chromadb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from llm_email_search.extract_emails_to_sqlite import Email
from chromadb.utils import embedding_functions


def embed_emails(sql_path, embeddings_path, model_name):
    """Embed emails from SQLite database into vector database.
    
    Args:
        sql_path (str): Path to SQLite database containing emails
        embeddings_path (str): Path to store embeddings database 
        model_name (str): Name of sentence transformer model to use
    """
    engine = create_engine(f"sqlite:///{sql_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    client = chromadb.PersistentClient(path=embeddings_path)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
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
                "timestamp": str(email.timestamp),  # Convert epoch milliseconds to string
                "attachment_types": email.attachment_types,
            }
        )
        ids.append(str(email.id))

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
    )


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

    embed_emails(args.sql_path, args.embeddings_path, args.model_name)


if __name__ == "__main__":
    main()
