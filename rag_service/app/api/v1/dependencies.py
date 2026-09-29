import chromadb
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.rag_services import CustomHTTPEmbeddings, DocumentService, RAGService

# Import your services and embedding class from their respective modules
# (Adjust imports based on your file structure, e.g., from app.services import ...)
# from .services import DocumentService, RAGService, CustomHTTPEmbeddings

security = HTTPBearer()

# ==========================================
# 1. User & Authentication Dependency
# ==========================================
class User:
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Validates the bearer token and returns the authenticated user.
    Replace this logic with your actual JWT decoding/validation.
    """
    token = credentials.credentials
    
    # MOCK USER VALIDATION FOR DEVELOPMENT:
    # In production, decode your JWT token here and extract user ID.
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Example mock user decoded from token
    # (e.g., if token is "user_123_token", user id becomes "user_123")
    user_id = token.split("_")[0] if "_" in token else "user_default"
    
    return User(id=user_id, email=f"{user_id}@example.com")


# ==========================================
# 2. Database & Infrastructure Dependencies
# ==========================================
def get_chroma_client() -> chromadb.ClientAPI:
    """Provides a persistent ChromaDB client instance."""
    # Uses a local folder 'chroma_storage' to save vectors across server restarts
    client = chromadb.PersistentClient(path="./chroma_storage")
    return client


def get_custom_embeddings() -> CustomHTTPEmbeddings:
    """Provides your custom HTTP embedding wrapper instance."""
    return CustomHTTPEmbeddings(api_url="http://localhost:8001/api/v1/ai/embedd")


# ==========================================
# 3. Service Layer Dependencies
# ==========================================
def get_document_service(
    chroma_client: chromadb.ClientAPI = Depends(get_chroma_client)
) -> DocumentService:
    """Injects ChromaDB client into the DocumentService."""
    return DocumentService(chroma_client=chroma_client)


def get_rag_service(
    chroma_client: chromadb.ClientAPI = Depends(get_chroma_client),
    embeddings = Depends(get_custom_embeddings)
) -> RAGService:
    """Injects ChromaDB client and embedding function into the RAGService."""
    return RAGService(chroma_client=chroma_client, embedding_function=embeddings)