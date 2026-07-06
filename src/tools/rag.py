# Vector DB & RAG Tool (For uploaded docs)
# src/tools/rag.py
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.tools import tool

# Directory to store the vector database
VECTOR_DB_DIR = "data/vector_db"
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# Initialize local, free embeddings (no Azure required)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize the Vector Store
vectorstore = Chroma(
    persist_directory=VECTOR_DB_DIR,
    embedding_function=embeddings
)

def ingest_pdf(file_path: str):
    """Loads a PDF, splits it into chunks, and saves it to the Vector DB."""
    print(f"[RAG] Ingesting PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # Split text into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    # Add to vector store
    vectorstore.add_documents(chunks)
    print(f" [RAG] Successfully added {len(chunks)} chunks to Vector DB.")

@tool
def query_uploaded_documents(query: str) -> str:
    """
    Searches the user's uploaded documents for specific information.
    Use this tool to find facts, data, or context from the PDFs the user provided.
    
    Args:
        query: The specific question or keyword to search for in the documents.
    """
    print(f"🔎 [RAG Tool] Querying Vector DB for: {query}")
    
    # Check if DB has any documents
    if not vectorstore.get()["ids"]:
        return "No documents have been uploaded yet."

    # Perform similarity search
    docs = vectorstore.similarity_search(query, k=3)
    
    if not docs:
        return "No relevant information found in the uploaded documents."
        
    # Format the results for the LLM
    formatted_results = []
    for i, doc in enumerate(docs):
        formatted_results.append(f"[Document Excerpt {i+1}] (Page {doc.metadata.get('page', 'Unknown')}):\n{doc.page_content}")
        
    return "\n\n---\n\n".join(formatted_results)