import argparse
import os

import chromadb
from chromadb.utils import embedding_functions
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from llm_email_search.extract_emails_to_sqlite import Email
from llm_email_search.logger import setup_logger

logger = setup_logger(__name__)


def embed_emails(
    sql_path: str, embeddings_path: str, model_name: str, batch_size: int = 2500,
    use_mps: bool = False
) -> None:
    """Embed emails from SQLite database into vector database.

    Args:
        sql_path (str): Path to SQLite database containing emails
        embeddings_path (str): Path to store embeddings database
        model_name (str): Name of sentence transformer model to use
        batch_size (int): Number of emails to embed at once
        use_mps (bool): Whether to use MPS (Metal Performance Shaders) for Apple Silicon
    """
    engine = create_engine(f"sqlite:///{sql_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Configure device for Apple Silicon if requested
    device_kwargs = {}
    if use_mps:
        try:
            import torch
            if torch.backends.mps.is_available():
                logger.info("Using MPS (Metal Performance Shaders) for Apple Silicon acceleration")
                device_kwargs = {"device": "mps"}
            else:
                logger.warning("MPS requested but not available. Using CPU instead.")
        except (ImportError, AttributeError):
            logger.warning("Could not import torch or MPS not supported. Using CPU instead.")

    client = chromadb.PersistentClient(path=embeddings_path)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name, **device_kwargs
    )
    collection = client.get_or_create_collection(
        "test_emails", embedding_function=sentence_transformer_ef
    )

    documents = []
    metadatas = []
    ids = []
    for email in session.query(Email).all():
        documents.append(email.body)
        if email.sender is None:
            logger.warning(f"Email {email.id} has no sender")
        if email.timestamp is None:
            logger.warning(f"Email {email.id} has no timestamp")
        metadatas.append(
            {
                "sender": str(email.sender),
                "subject": str(email.subject),
                "timestamp": str(
                    email.timestamp
                ),  # Convert epoch milliseconds to string
                "attachment_types": str(email.attachment_types),
            }
        )
        ids.append(str(email.id))
    logger.info(f"Embedding {len(documents)} emails")

    for i in tqdm(range(0, len(documents), batch_size)):
        collection.add(
            documents=documents[i : min(i + batch_size, len(documents))],
            metadatas=metadatas[i : min(i + batch_size, len(metadatas))],
            ids=ids[i : min(i + batch_size, len(ids))],
        )
    logger.info(
        f"Embedding is complete. Collection now contains {collection.count()} embedded emails"
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
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2500,
        help="Batch size for embedding inference (default: 2500)",
    )
    parser.add_argument(
        "--use-mps",
        action="store_true",
        help="Use MPS (Metal Performance Shaders) for Apple Silicon acceleration",
    )
    args = parser.parse_args()
    if not os.path.exists(args.sql_path):
        raise FileNotFoundError(f"SQLite database file not found at {args.sql_path}")

    embed_emails(args.sql_path, args.embeddings_path, args.model_name, args.batch_size, args.use_mps)


if __name__ == "__main__":
    main()
