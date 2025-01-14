import pytest
from llm_email_search.run_query import run_query

def test_run_query(sample_db_with_emails, temp_embeddings_path):
    # First embed the emails
    from llm_email_search.embed_emails import embed_emails
    embed_emails(
        sample_db_with_emails,
        temp_embeddings_path,
        "sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Test the query functionality
    results = run_query(
        query="test email",
        num_results=2,
        embeddings_path=temp_embeddings_path
    )
    
    assert len(results['ids'][0]) == 2
    assert 'metadatas' in results
    assert 'distances' in results
    assert len(results['metadatas'][0]) == 2
    assert len(results['distances'][0]) == 2

def test_run_query_with_invalid_path():
    with pytest.raises(FileNotFoundError):
        run_query(
            query="test",
            embeddings_path="nonexistent_path.db"
        ) 