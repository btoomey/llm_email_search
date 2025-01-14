import argparse
import os

import chromadb
from chromadb.utils import embedding_functions

from llm_email_search.logger import setup_logger

logger = setup_logger(__name__)

def run_query(query: str, num_results: int = 2, embeddings_path: str = "embedded_emails.db") -> dict:
    """Search emails using semantic similarity to a query string.
    
    Args:
        query (str): The search query text to match against email content
        num_results (int, optional): Number of most similar results to return. Defaults to 2.
        embeddings_path (str, optional): Path to ChromaDB embeddings database. Defaults to "embedded_emails.db".
    
    Returns:
        dict: Query results containing:
            - ids: List of email IDs for matches
            - distances: List of similarity scores
            - metadatas: List of email metadata (sender, subject, timestamp, attachments)
            
    Raises:
        FileNotFoundError: If embeddings database not found at specified path
    """
    # Check if the embeddings database exists
    if not os.path.exists(embeddings_path):
        logger.error(f"Embeddings database not found at {embeddings_path}")
        raise FileNotFoundError(f"Embeddings database not found at {embeddings_path}")

    logger.info(f"Connecting to embeddings database at {embeddings_path}")
    client = chromadb.PersistentClient(path=embeddings_path)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        "test_emails", embedding_function=sentence_transformer_ef
    )
    
    logger.info(f"Running query: '{query}' with {num_results} results requested")
    results = collection.query(
        query_texts=[query],
        n_results=num_results,
    )
    
    logger.info(f"Found {len(results['ids'][0])} matching results")
    return results

def main():
    parser = argparse.ArgumentParser(description="Search emails using semantic search")
    parser.add_argument(
        "query",
        type=str,
        help="Search query text"
    )
    parser.add_argument(
        "--num-results",
        type=int,
        default=2,
        help="Number of results to return (default: 2)"
    )
    parser.add_argument(
        "--embeddings-path",
        type=str,
        default="embedded_emails.db",
        help="Path to store embeddings database (default: embedded_emails.db)",
    )
    args = parser.parse_args()

    try:
        results = run_query(
            query=args.query,
            num_results=args.num_results,
            embeddings_path=args.embeddings_path
        )
        logger.info("Query results:")
        logger.info(results)
    except Exception as e:
        logger.error(f"Error running query: {str(e)}")
        raise

if __name__ == "__main__":
    main()
