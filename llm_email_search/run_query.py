import argparse
import os
import chromadb
from chromadb.utils import embedding_functions

def run_query(query, num_results=2, embeddings_path="embedded_emails.db"):
    # Check if the embeddings database exists
    if not os.path.exists(embeddings_path):
        raise FileNotFoundError(f"Embeddings database not found at {embeddings_path}")

    client = chromadb.PersistentClient(path=embeddings_path)
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        "test_emails", embedding_function=sentence_transformer_ef
    )

    results = collection.query(
        query_texts=[query],
        n_results=num_results,
    )

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

    results = run_query(
        query=args.query,
        num_results=args.num_results,
        embeddings_path=args.embeddings_path
    )
    
    print(results)

if __name__ == "__main__":
    main()
