import chromadb
import warnings
from rank_bm25 import BM25Okapi
# from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader,TextLoader
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from langsmith import Client
from dotenv import load_dotenv


#grader llm set up and dataset creation
client = Client()
# grader_llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite",temperature=0)

dataset_name = "RAG Test Evaluation"

#  Check and create dataset if missing
if not client.has_dataset(dataset_name=dataset_name):
    print(f"Dataset '{dataset_name}' not found. Creating it now...")
    
    # Define test examples
    examples = [
    {
        "inputs": {"question": "What does error code ERR_401 mean ?"},
        "outputs": {"answer": "ERR_401 indicates missing Local Administrator permission."}
    },
    {
        "inputs": {"question": "There is a issue connecting wifi to my laptop, what should I do?"},
        "outputs": {"answer": """To resolve the issue with your laptop not connecting to the office WiFi, you should
                   Verify that your WiFi is enabled,Forget the network and reconnect to it,
                    Check to ensure your VPN is disconnected,Restart your laptop,
                    Contact IT if the issue persists."""}
    },
    {
        "inputs": {"question": "What is the Password Reset Policy?"},
        "outputs": {"answer": """Employees must reset their password every 90 days.
                         first Open Self Service Portal,then Click Reset Password,nextFollow MFA verification.
                         the Policy ID is HR-POL-2023-14"""}
    },
    {
        "inputs": {"question": "What is java?"},
        "outputs": {"answer": """Java is a high-level, class-based, object-oriented programming language that is designed to have as few implementation dependencies as possible.
        """}
    }
]
    
    # Create dataset and add examples
    dataset = client.create_dataset(dataset_name=dataset_name)
    client.create_examples(
        inputs=[e["inputs"] for e in examples],
        outputs=[e["outputs"] for e in examples],
        dataset_id=dataset.id
    )
    print("Dataset created successfully!")
else:
    print(f"Dataset '{dataset_name}' found.")


#pydantic schema for structural output
class CorrectnessGrade(BaseModel):
    explanation: str = Field(description="Step-by-step reasoning for the score")
    correct: bool = Field(description="True if student answer matches ground truth factually, False otherwise")

class RelevanceGrade(BaseModel):
    explanation: str = Field(description="Step-by-step reasoning for the score")
    relevant: bool = Field(description="True if answer directly addresses the question, False otherwise")

class GroundedGrade(BaseModel):
    explanation: str = Field(description="Step-by-step reasoning for the score")
    grounded: bool = Field(description="True if answer contains no hallucinations outside facts, False otherwise")

class RetrievalRelevanceGrade(BaseModel):
    explanation: str = Field(description="Step-by-step reasoning for the score")
    relevant: bool = Field(description="True if retrieved facts contain relevant keywords or semantic context")


 ### Evaluator Functions (Configured for LangSmith Metrics UI)

# def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:  ### output vs reference_output
#     answer = outputs.get("answer", str(outputs))
#     prompt = f"QUESTION: {inputs['question']}\nGROUND TRUTH: {reference_outputs['answer']}\nANSWER: {answer}"
#     grader = grader_llm.with_structured_output(CorrectnessGrade)
#     result = grader.invoke(prompt)
#     return {"key": "correctness", "score": result.correct, "comment": result.explanation}

# def relevance(inputs: dict, outputs: dict) -> dict:          ### input vs output
#     answer = outputs.get("answer", str(outputs))
#     prompt = f"QUESTION: {inputs['question']}\nANSWER: {answer}"
#     grader = grader_llm.with_structured_output(RelevanceGrade)
#     result = grader.invoke(prompt)
#     return {"key": "relevance", "score": result.relevant, "comment": result.explanation}

# def groundedness(inputs: dict, outputs: dict) -> dict:     ### ground truth  vs output 
#     docs = outputs.get("documents", [])
#     docs_text = "\n\n".join(doc.page_content if isinstance(doc, Document) else str(doc) for doc in docs)
#     answer = outputs.get("answer", str(outputs))
    
#     prompt = f"FACTS: {docs_text}\nANSWER: {answer}"
#     grader = grader_llm.with_structured_output(GroundedGrade)
#     result = grader.invoke(prompt)
#     return {"key": "groundedness", "score": result.grounded, "comment": result.explanation}

# def retrieval_relevance(inputs: dict, outputs: dict) -> dict:    ### input vs retreived docs
#     docs = outputs.get("documents", [])
#     docs_text = "\n\n".join(doc.page_content if isinstance(doc, Document) else str(doc) for doc in docs)
    
#     prompt = f"FACTS: {docs_text}\nQUESTION: {inputs['question']}"
#     grader = grader_llm.with_structured_output(RetrievalRelevanceGrade)
#     result = grader.invoke(prompt)
#     return {"key": "retrieval_relevance", "score": result.relevant, "comment": result.explanation}

#target function for evaluation
# def target(inputs: dict) -> dict:
#     query = inputs["question"]

#     retrieved_docs = hybrid_retrieve(query)  # Returns list[Document] or list[str]
#     answer = answer_question(query)          # Returns str answer
    
#     return {
#         "answer": answer,
#         "documents": retrieved_docs
#     }


# experiment_results = client.evaluate(
#     target,
#     data="RAG Test Evaluation",
#     evaluators=[correctness, groundedness, relevance, retrieval_relevance],
#     experiment_prefix="hybrid-rag-gemini-eval"
# )