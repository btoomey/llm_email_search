import chromadb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from extract_emails_to_sqlite import Email
from chromadb.utils import embedding_functions


def main():
    # Initialize SQLAlchemy session
    engine = create_engine("sqlite:///emails.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    client = chromadb.PersistentClient(path="embedded_emails.db")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"#, trust_remote_code=True
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
