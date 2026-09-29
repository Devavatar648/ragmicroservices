import requests
from langchain_core.embeddings import Embeddings
import os
import shutil
import uuid
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import chromadb
import requests
import chromadb
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document

class CustomHTTPEmbeddings(Embeddings):
    """Custom embedding class that calls your local FastAPI embedding endpoint."""
    def __init__(self, api_url: str = "http://localhost:8001/api/v1/ai/embedd"):
        self.api_url = api_url

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        response = requests.post(self.api_url, json=texts)
        response.raise_for_status()
        result = response.json()
        # Adjust depending on whether your API returns {"embeddings": [...]} or just the list
        return result.get("embeddings", result)

    def embed_query(self, text: str) -> list[float]:
        response = requests.post(self.api_url, json=[text])
        response.raise_for_status()
        result = response.json()
        embeddings = result.get("embeddings", result)
        return embeddings[0]
    
class DocumentService:
    def __init__(self, chroma_client: chromadb.ClientAPI):
        self.chroma_client = chroma_client
        self.embeddings = CustomHTTPEmbeddings()

    def process_and_store_document(self, file: UploadFile, user_id: str):
        # Step 1: Get document & save temporarily
        temp_file_path = f"temp_{uuid.uuid4()}_{file.filename}"
        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Step 2: Load documents using LangChain document loaders based on file type
            if file.filename.endswith(".pdf"):
                loader = PyPDFLoader(temp_file_path)
            elif file.filename.endswith(".txt"):
                loader = TextLoader(temp_file_path, encoding="utf-8")
            else:
                raise ValueError("Unsupported file format. Only PDF and TXT are supported.")
            
            raw_documents = loader.load()

            # Step 3: Split the document into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=700,
                chunk_overlap=100
            )
            split_docs = text_splitter.split_documents(raw_documents)

            # Inject user_id into metadata for secure multi-tenant filtering later
            for doc in split_docs:
                doc.metadata["user_id"] = user_id
                doc.metadata["source_file"] = file.filename

            # Step 4: Store into ChromaDB vector store
            # (LangChain's Chroma vectorstore will automatically call your custom 
            #  http://localhost:8001/api/v1/ai/embedd endpoint under the hood via embed_documents)
            vector_store = Chroma(
                client=self.chroma_client,
                collection_name="user_documents_pool", # Shared collection for all users
                embedding_function=self.embeddings
            )

            vector_store.add_documents(split_docs)

            return {
                "status": "success",
                "message": f"Successfully processed {len(split_docs)} chunks from {file.filename}",
                "user_id": user_id
            }

        finally:
            # Clean up the temporary file from the server disk
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

class RAGService:
    def __init__(self, chroma_client: chromadb.ClientAPI, embedding_function):
        self.chroma_client = chroma_client
        self.embeddings = embedding_function
        self.collection_name = "user_documents_pool"
        self.chat_endpoint = "http://localhost:8001/api/v1/ai/chat"

    def answer_query(self, user_id: str, query: str) -> dict:
        # Step 1: Initialize ChromaDB retriever with strict user metadata filter
        vector_store = Chroma(
            client=self.chroma_client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
        
        chroma_retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 4,
                "filter": {"user_id": user_id}  # <--- Ensures user isolation
            }
        )

        # Step 2: Initialize BM25 retriever scoped ONLY to this user's documents
        # Fetching user-specific docs from Chroma storage to build a private BM25 index
        collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
        user_data = collection.get(where={"user_id": user_id})
        
        texts = user_data.get("documents", [])
        metadatas = user_data.get("metadatas", [])

        if not texts:
            return {
                "response": "No documents found for this user. Please upload a document first.",
                "context": ""
            }

        user_documents = [
            Document(page_content=text, metadata=meta) 
            for text, meta in zip(texts, metadatas)
        ]
        
        bm25_retriever = BM25Retriever.from_documents(user_documents)
        bm25_retriever.k = 4

        # Step 3: Use EnsembleRetriever combining Chroma (Vector) and BM25 (Keyword)
        ensemble_retriever = EnsembleRetriever(
            retrievers=[chroma_retriever, bm25_retriever],
            weights=[0.5, 0.5]  # Equal weight for semantic and keyword search
        )

        # Step 4: Get context of the query
        retrieved_docs = ensemble_retriever.invoke(query)
        
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        

        # Step 5: Post the context and query to the chat endpoint
        payload = {
            "prompt": query,
            "context": context
        }

        print(payload)
        
        response = requests.post(self.chat_endpoint, json=payload)
        response.raise_for_status()
        
        # Step 6: Return the response
        return response.json()