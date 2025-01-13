import argparse
import chromadb
from chromadb.utils import embedding_functions

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
    args = parser.parse_args()

    client = chromadb.PersistentClient(path="embedded_emails.db")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-MiniLM-L6-v2"#, trust_remote_code=True
    )
    collection = client.get_or_create_collection(
        "test_emails", embedding_function=sentence_transformer_ef
    )

    results = collection.query(
        query_texts=[args.query],
        n_results=args.num_results,
    )

    print(results)


if __name__ == "__main__":
    main()
