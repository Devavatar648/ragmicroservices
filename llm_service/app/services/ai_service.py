from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langsmith import traceable
import truststore
import numpy as np

from app.core.exceptions import ExceptionHandler

class AIService:

    truststore.inject_into_ssl()
    def __init__(self, google_api_key:str=None, embedding_model:str='models/gemini-embedding-001', chat_model_name:str='gemini-3.5-flash-lite'):
        self.embeddings_model = GoogleGenerativeAIEmbeddings(
            model=embedding_model, 
            google_api_key=google_api_key
        )
        self.chat_model = ChatGoogleGenerativeAI(
            google_api_key=google_api_key,
            model=chat_model_name
        )

    def generate_embiddings(self, texts: list[str])->list[list[float]]:
        """
            Generate embeddings for a list of texts using Google Generative AI

            Args:
                texts: List of text strings to embed

            Returns:
                numpy array of embeddings with shape (len(texts), embedding_dim)
        """
        if not self.embeddings_model:
            raise ExceptionHandler('Embidding model not initialize...')
        
        if not texts:
            return np.empty((0, 768))
        
        embeddings_array = np.empty((0, 768))

        try:
            print(f"Generate embidding for {len(texts)} texts.")

            # Batch embed documents using LangChain's Google integration
            raw_embeddings = self.embeddings_model.embed_documents(texts)

        except Exception as e:
            raise ExceptionHandler(f"Error while embidding: {e}")

        return {"embeddings": raw_embeddings}
    
    # Add decorator so this function is traced in LangSmith
    @traceable()
    def generate_response(self, context:str, query:str):
        """Generate response from the given context"""

        prompt = """
                        You are an assistant that answers questions using only the retrieved context below. 
                        If the context does not contain enough information to address the prompt, 
                        politely state: 'I'm sorry, but this topic is outside the scope of the provided information.

                        context : {context}

                        question: {query}

                        answer:
                    """
        result = self.chat_model.invoke([prompt.format(context=context, query=query)])
        return {"answer": result.content[0]['text'], "documents": context}