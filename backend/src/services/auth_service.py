"""
Authentication service - xử lý đăng nhập, đăng ký, JWT
"""
from datetime import datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models import User, UserRole
from src.schemas import Token, UserRegister

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service xử lý authentication"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Băm password"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Kiểm tra password"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user_id: UUID, role: UserRole) -> str:
        """Tạo JWT token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": str(user_id),
            "role": role.value,
            "exp": expire
        }
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """Lấy user theo email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
        """Lấy user theo ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def register(db: AsyncSession, data: UserRegister) -> User:
        """Đăng ký user mới"""
        # Kiểm tra email đã tồn tại
        existing = await AuthService.get_user_by_email(db, data.email)
        if existing:
            raise ValueError("Email đã được sử dụng")

        # Tạo user mới
        user = User(
            email=data.email,
            password_hash=AuthService.hash_password(data.password),
            name=data.name,
            phone=data.phone,
            role=UserRole.CUSTOMER
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> Token | None:
        """Đăng nhập"""
        user = await AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None

        access_token = AuthService.create_access_token(user.id, user.role)
        return Token(access_token=access_token)

    @staticmethod
    async def verify_token(token: str) -> dict | None:
        """Xác thực token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
