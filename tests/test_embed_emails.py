import chromadb
from llm_email_search.embed_emails import embed_emails


def test_embed_emails(sample_db_with_emails, temp_embeddings_path):
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    # Embed the emails
    embed_emails(sample_db_with_emails, temp_embeddings_path, model_name)

    # Verify the embeddings database was created
    client = chromadb.PersistentClient(path=temp_embeddings_path)
    collection = client.get_collection("test_emails")

    # Query to verify the embeddings
    results = collection.query(query_texts=["test email"], n_results=2)

    # The results["ids"] is a list of lists, so we need to check the length of the first list
    assert len(results["ids"][0]) == 2
