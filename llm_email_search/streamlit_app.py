import streamlit as st
from llm_email_search.extract_emails_to_sqlite import extract_emails
from llm_email_search.embed_emails import embed_emails
from llm_email_search.run_query import run_query
import os
import torch

# Hack to prevent torch/Streamlit issues 
# (see here: https://discuss.streamlit.io/t/error-in-torch-with-streamlit/90908/4)
torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)]

st.title("LLM Email Search")

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Extract Emails", "Embed Emails", "Search Emails"])

with tab1:
    st.header("Extract Emails")
    num_emails = st.number_input(
        "Number of emails to extract", min_value=1, max_value=10000, value=100
    )
    extract_path = st.text_input(
        "Path to save the emails", value="emails.db", key="extract_path"
    )
    if st.button("Extract Emails"):
        with st.spinner("Extracting emails..."):
            extract_emails(num_emails, extract_path)
        st.success("Emails extracted successfully")

with tab2:
    st.header("Embed Emails")
    emails_path = st.text_input(
        "Path to the emails", value="emails.db", key="emails_path"
    )
    embeddings_path = st.text_input(
        "Path to save the embeddings", value="embeddings.db"
    )
    model_name = st.text_input(
        "Name of embedding model to use", value="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Add a checkbox to force CPU usage
    use_cpu = st.checkbox("Force CPU usage (may help with memory issues)", value=False)

    if st.button("Embed Emails"):
        with st.spinner("Embedding emails..."):
            try:
                # Set CUDA_VISIBLE_DEVICES to empty if use_cpu is checked
                if use_cpu:
                    os.environ["CUDA_VISIBLE_DEVICES"] = ""
                    st.info("Using CPU for embeddings (GPU disabled)")

                # Run in a separate process to avoid memory issues
                embed_emails(emails_path, embeddings_path, model_name)
                st.success("Emails embedded successfully")
            except Exception as e:
                st.error(f"Error embedding emails: {str(e)}")
                st.error("Stack trace:", exc_info=True)

with tab3:
    st.header("Search Emails")
    query = st.text_input("Query to search for")
    num_results = st.number_input(
        "Number of results to return", min_value=1, max_value=100, value=10
    )
    if st.button("Search Emails"):
        if not query:
            st.warning("Please enter a query to search for")
        else:
            with st.spinner("Searching emails..."):
                try:
                    results = run_query(query, num_results)
                    st.success("Emails searched successfully")
                    if results and "documents" in results:
                        with st.expander("Results", expanded=True):
                            for i, result in enumerate(results["documents"]):
                                st.markdown(f"**Result {i+1}**")
                                st.write(result)
                                st.divider()
                    else:
                        st.info("No results found")
                except Exception as e:
                    st.error(f"Error searching emails: {str(e)}")
