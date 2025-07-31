# Required imports
import os
import uuid
from sqlalchemy import create_engine
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    SQLDatabase,
    PromptTemplate,
    StorageContext,
)
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool, FunctionTool
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.readers.docling import DoclingReader
from llama_index.vector_stores.milvus import MilvusVectorStore
from cleanlab_codex.project import Project
from cleanlab_codex.client import Client


#####################################
# Define Tools for Router Agent
#####################################
def create_codex_project():
    """Create a Codex project for document validation."""
    try:
        # Check if CODEX_API_KEY is available
        if not os.environ.get("CODEX_API_KEY"):
            print(
                "Warning: CODEX_API_KEY not found. Codex validation will be disabled."
            )
            return None

        # Create a unique identifier for the project
        project_id = str(uuid.uuid4())[:8]  # Using first 8 chars for readability

        codex_client = Client()
        project = codex_client.create_project(name=f"RAG + SQL Router {project_id}")
        access_key = project.create_access_key("default key")
        project = Project.from_access_key(access_key)
        return project
    except Exception as e:
        print(f"Error creating Codex project: {e}")
        return None


# Global variables for reuse
docs_query_engine = None
codex_project = None


def setup_sql_tool():
    """Setup SQL query tool for querying city database."""
    # Setup SQLite database
    db_path = "city_database.sqlite"
    engine = create_engine(f"sqlite:///{db_path}")
    sql_database = SQLDatabase(engine)

    # Create SQL query engine
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"],
    )

    # Create tool for SQL querying
    sql_tool = QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        name="sql_tool",
        description=(
            "Useful for translating a natural language query into a SQL query over"
            " a table containing: city_stats, containing the population/state of"
            " each city located in the USA."
        ),
    )

    # Return the SQL tool
    return sql_tool


def setup_document_tool(file_dir):
    """Setup document query tool from uploaded documents with Codex validation."""
    global docs_query_engine, codex_project

    # Create a reader and load the data
    reader, node_parser = DoclingReader(), MarkdownNodeParser()
    loader = SimpleDirectoryReader(
        input_dir=file_dir,
        file_extractor={
            ".pdf": reader,
            ".docx": reader,
            ".pptx": reader,
            ".txt": reader,
        },
    )
    docs = loader.load_data()

    # Creating a vector index over loaded data
    unique_collection_id = uuid.uuid4().hex
    collection_name = f"rag_with_sql_{unique_collection_id}"
    vector_store = MilvusVectorStore(uri="http://localhost:19530", dim=384, overwrite=True, collection_name=collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    vector_index = VectorStoreIndex.from_documents(
        docs,
        show_progress=True,
        transformations=[node_parser],
        storage_context=storage_context,
    )

    # Custom prompt template
    template = (
        "You are a meticulous and accurate document analyst. Your task is to answer the user's question based exclusively on the provided context. "
        "Follow these rules strictly:\n"
        "1. Your entire response must be grounded in the facts provided in the 'Context' section. Do not use any prior knowledge.\n"
        "2. If multiple parts of the context are relevant, synthesize them into a single, coherent answer.\n"
        "3. If the context does not contain the information needed to answer the question, you must state only: 'The provided context does not contain enough information to answer this question.'\n"
        "-----------------------------------------\n"
        "Context: {context_str}\n"
        "-----------------------------------------\n"
        "Question: {query_str}\n\n"
        "Answer:"
    )
    qa_template = PromptTemplate(template)

    # Create a query engine for the vector index
    docs_query_engine = vector_index.as_query_engine(
        text_qa_template=qa_template, similarity_top_k=3
    )

    # Initialize Codex project
    codex_project = create_codex_project()

    # Define the document query function with Codex validation
    def document_query_tool(query: str):
        """Query documents with Codex validation for enhanced accuracy."""
        # Step 1: Query the engine
        response_obj = docs_query_engine.query(query)
        initial_response = str(response_obj)

        # Step 2: Gather source context
        context = response_obj.source_nodes
        context_str = "\n".join([n.node.text for n in context])

        # Step 3: Prepare prompt for Codex validation
        user_prompt = template.format(context_str=context_str, query_str=query)
        messages = [{"role": "user", "content": user_prompt}]

        # Step 4: Validate with Codex (if available)
        if codex_project:
            try:
                result = codex_project.validate(
                    messages=messages,
                    query=query,
                    context=context_str,
                    response=initial_response,
                )

                # Step 5: Final response selection
                fallback_response = "I'm sorry, I couldn't find an answer — can I help with something else?"
                final_response = (
                    result.expert_answer
                    if result.expert_answer and result.escalated_to_sme
                    else (
                        fallback_response
                        if result.should_guardrail
                        else initial_response
                    )
                )
                trust_score = result.model_dump()["eval_scores"]["trustworthiness"]["score"]

                # Return a dictionary to avoid tuple handling issues
                return {
                    "response": str(final_response),
                    "trust_score": float(trust_score)
                }
            except Exception as e:
                # If Codex validation fails, return the initial response
                print(f"Codex validation failed: {e}")
                return {
                    "response": str(initial_response),
                    "trust_score": None
                }
        else:
            # If Codex is not available, return the initial response
            print("Codex not available, using basic RAG response")
            return {
                "response": str(initial_response),
                "trust_score": None
            }

    # Create tool for document querying using FunctionTool
    docs_tool = FunctionTool.from_defaults(
        document_query_tool,
        name="document_tool",
        description=(
            "Useful for answering a natural language question by performing a semantic search over "
            "a collection of documents. These documents may contain general knowledge, reports, "
            "or domain-specific content. Returns the most relevant passages or synthesized answers. "
            "If the user query does not relate to US city statistics (population and state), use this document search tool."
        ),
    )

    # Return the document tool
    return docs_tool
