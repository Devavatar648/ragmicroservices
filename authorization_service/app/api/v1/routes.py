from fastapi import APIRouter, Depends, status

from app.schemas.user import UserCreate, LoginRequest, LoginResponse, UserResponse, UserUpdate

from app.services.user_service import UserService
from app.api.v1.dependencies import get_user_service

router = APIRouter(
    prefix='/user',
    tags=['users']
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, service: UserService = Depends(get_user_service)):
    return service.create_user(user_data)

@router.get("/", response_model=list[UserResponse])
def get_users(service:UserService = Depends(get_user_service)):
    return service.get_users()

@router.post('/login', response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(login_data:LoginRequest, service:UserService = Depends(get_user_service))->UserResponse:
    return service.login(login_data)

@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id:str, service:UserService = Depends(get_user_service))->UserResponse:
    return service.get_user_details(user_id)

@router.patch('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user_by_id(user_id:str, user_data:UserUpdate, service:UserService = Depends(get_user_service))->UserResponse:
    return service.update_user(user_id, user_data)
