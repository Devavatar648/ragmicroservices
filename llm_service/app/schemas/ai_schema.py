from pydantic import Field, BaseModel, ConfigDict

class AIChatResponse(BaseModel):
    answer: str
    documents: str

    model_config = ConfigDict(
        from_attributes=True
    )

class ChatRequest(BaseModel):
    prompt: str
    context: str
