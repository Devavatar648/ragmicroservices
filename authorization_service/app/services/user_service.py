import bcrypt

from app.models.user import User
from app.repositories.user_repositories import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse, LoginRequest, LoginResponse
from app.core.exceptions import UserNotFoundException, ExceptionHandler


class PasswordService:
    
    def get_hash_password(self, password:str)->str:
        """Hash a plain text password for storing in the database."""
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode("utf-8")

    def compare_password(self, plain_password:str, hashed_password: str)->bool:
        """Verify a plain text password against the stored database hash."""
        pwd_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)

class UserService:

    def __init__(self, repository:UserRepository):
        self.repository = repository
        self.password_service = PasswordService()

    def create_user(self, user:UserCreate)->User:

        user = User(
            email=user.email,
            password=self.password_service.get_hash_password(user.password)
        )

        return self.repository.create_user(user)
    
    def login(self, user:LoginRequest)->User:
        user_data: User = self.repository.get_user_by_email(user.email)

        if not user_data:
            raise UserNotFoundException(user.email)
        
        if not self.password_service.compare_password(user.password, user_data.password):
            raise ExceptionHandler('Invalid email or password')
    
        return user_data
        
    
    def get_users(self)->list[UserResponse]:
        return self.repository.get_all_users()
    
    def get_user_details(self, user_id:str)->User:
        return self.repository.get_user_by_userId(user_id)
    
    def update_user(self, user_id:str, user_update:UserUpdate)->UserResponse:
        # 1. Check if user exists
        db_user = self.repository.get_user_by_userId(user_id)
        if not db_user:
            raise UserNotFoundException(user_id)  # Or raise a custom HTTP exception

        # 2. Convert Pydantic model to dict, excluding unset fields
        update_data = user_update.model_dump(exclude_unset=True)

        # 3. Business Logic: If password is being updated, hash it first!
        if "password" in update_data:
            update_data["password"] = self.password_service.get_hash_password(update_data["password"])

        # 4. Pass clean data to the repository
        return self.repository.update_user(db_user, update_data)



