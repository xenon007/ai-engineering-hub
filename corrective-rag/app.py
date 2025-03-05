import nest_asyncio
nest_asyncio.apply()

from dotenv import load_dotenv
load_dotenv()

import logging
import sys
import os
import asyncio
import streamlit as st
import qdrant_client
from IPython.display import Markdown, display
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from workflow import CorrectiveRAGWorkflow

# Set up page configuration
st.set_page_config(page_title="Corrective RAG Demo", layout="wide")
st.title("Corrective RAG Workflow Demo")

# Initialize session state to store the workflow
if "workflow" not in st.session_state:
    st.session_state.workflow = None

# Function to initialize the workflow
def initialize_workflow():
    with st.spinner("Loading documents and initializing the workflow..."):
        documents = SimpleDirectoryReader("./docs").load_data()
        
        client = qdrant_client.QdrantClient(
            host="localhost",
            port=6333
        )
        
        vector_store = QdrantVectorStore(client=client, collection_name="test")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )
        
        workflow = CorrectiveRAGWorkflow(
            index=index, 
            linkup_api_key=os.environ["LINKUP_API_KEY"], 
            verbose=True, 
            timeout=60
        )
        
        st.session_state.workflow = workflow
        st.success("Workflow initialized successfully!")

# Function to run the async workflow
async def run_workflow(query):
    return await st.session_state.workflow.run(query_str=query)

# Initialize the workflow if not already done
if st.session_state.workflow is None:
    initialize_workflow()

# Create the query input
query = st.text_input("Enter your question:", placeholder="How was Llama2 pretrained?")

# Run button
if st.button("Run Query") and query:
    if st.session_state.workflow:
        with st.spinner("Processing your query..."):
            # Run the async workflow in a way that works with Streamlit
            result = asyncio.run(run_workflow(query))
            st.markdown(result)
    else:
        st.error("Workflow not initialized. Please refresh the page.")

# Add some example queries
st.sidebar.header("Example Queries")
example_queries = [
    "How was Llama2 pretrained?",
    "What are the key components of the architecture?",
    "Explain the training process for the model."
]

for example in example_queries:
    if st.sidebar.button(example):
        # This will set the query in the text input
        st.session_state.query = example
        st.rerun()

# If there's a query in the session state, use it
if "query" in st.session_state:
    query = st.session_state.query
    # Clear it so it doesn't keep running
    del st.session_state.query