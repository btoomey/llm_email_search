# llm_email_search
A repository that allows the user to search their emails with natural language queries using LLMs. For now, it only works with Gmail.

## Pre-requisites
- Python 3.12+
- Poetry
- Gmail API access ([see here](https://developers.google.com/gmail/api/quickstart/python) for more details on setting it up)
- Google API OAuth2 credentials.json or token.pickle

## Basic usage

1. Run `poetry install` to install the dependencies
2. Run `poetry run python llm_email_search/extract_emails_to_sqlite.py` to extract emails to a SQLite database. Available arguments: 
    - `--database` (path to SQLite database, set to `emails.db` by default)
    - `--max-emails` (number of emails to extract, set to `1000` by default)
3. Run `poetry run python llm_email_search/embed_emails.py` to embed the emails into a vector database. Available arguments: 
    - `--embeddings-path` (path to vector database, set to `emails_embeddings.db` by default)
    - `--model-name` (name of sentence transformer model, set to `sentence-transformers/all-MiniLM-L6-v2` by default)
    - `--sql-path` (path to SQLite database, set to `emails.db` by default)
4. Run `poetry run python llm_email_search/run_query.py` to run a query on the vector database. Available arguments: 
    - `--embeddings-path` (path to vector database, set to `emails_embeddings.db` by default)
    - `--num-results` (number of results to return, set to `2` by default)
    - `query` (query text, no default value)

## Notes
- Currently, the `run_query.py` script only supports the `sentence-transformers/all-MiniLM-L6-v2` model. Other embeddings are on the roadmap but not yet implemented.
- The codebase currently performs a direct semantic search based on your search string. A future version will support a more complex query system that allows for more complex queries (eg. "emails from John that contain an image attachment and were sent in the last week").