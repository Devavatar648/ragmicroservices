from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):

    email : str = Field(
        min_length=5
    )

    password: str = Field(
        min_length=6,
        max_length=12
    )


class UserUpdate(BaseModel):

    email : str | None = Field(
        default=None,
        min_length=5
    )

    password: str | None = Field(
        default=None,
        min_length=6,
        max_length=12
    )

    is_active : bool | None = None

    total_query : int | None = Field(
        default=None,
        ge=0
    )

class UserResponse(BaseModel):
    id: str
    email : str
    role : str
    is_active: bool
    total_query : int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class LoginRequest(UserCreate):
    pass

class LoginResponse(BaseModel):
    id: str
    email : str
    role : str


    model_config = ConfigDict(
        from_attributes=True
    )