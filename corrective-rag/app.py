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
import base64
import gc
import tempfile
import uuid
from IPython.display import Markdown, display
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from workflow import CorrectiveRAGWorkflow

# Set up page configuration
st.set_page_config(page_title="Corrective RAG Demo", layout="wide")

# Initialize session state variables
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}
    
if "workflow" not in st.session_state:
    st.session_state.workflow = None
    
if "messages" not in st.session_state:
    st.session_state.messages = []

session_id = st.session_state.id

def reset_chat():
    st.session_state.messages = []
    gc.collect()

def display_pdf(file):
    st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:100vh; width:100%"
                    >
                    </iframe>"""

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

# Function to initialize the workflow with uploaded documents
def initialize_workflow(file_path):
    with st.spinner("Loading documents and initializing the workflow..."):
        documents = SimpleDirectoryReader(file_path).load_data()
        
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
        return workflow

# Function to run the async workflow
async def run_workflow(query):
    return await st.session_state.workflow.run(query_str=query)

# Sidebar for document upload
with st.sidebar:
    st.header("Add your documents!")
    
    uploaded_file = st.file_uploader("Choose your `.pdf` file", type="pdf")

    if uploaded_file:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                file_key = f"{session_id}-{uploaded_file.name}"
                st.write("Indexing your document...")

                if file_key not in st.session_state.get('file_cache', {}):
                    # Initialize workflow with the uploaded document
                    workflow = initialize_workflow(temp_dir)
                    st.session_state.file_cache[file_key] = workflow
                else:
                    st.session_state.workflow = st.session_state.file_cache[file_key]

                # Inform the user that the file is processed and Display the PDF uploaded
                st.success("Ready to Chat!")
                display_pdf(uploaded_file)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

# Main chat interface
col1, col2 = st.columns([6, 1])

with col1:
    st.header("Corrective RAG Chat")

with col2:
    st.button("Clear ↺", on_click=reset_chat)

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        if st.session_state.workflow:
            message_placeholder = st.empty()
            full_response = ""
            
            # Run the async workflow
            result = asyncio.run(run_workflow(prompt))
            message_placeholder.markdown(result)
            full_response = result
        else:
            full_response = "Please upload a document first to initialize the workflow."
            st.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})