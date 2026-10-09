"""
User Context - Extract user identity từ authenticated context

Đây là abstraction nhỏ nhất để lấy user identity.
Role và user_id phải đến từ authenticated context (JWT token),
không tin user input tùy ý.
"""
from dataclasses import dataclass
from typing import Any

from src.ai.security.tool_guard import Role


@dataclass
class UserContext:
    """
    User context từ authenticated request.

    Attributes:
        user_id: UUID của user (từ JWT token)
        role: Role của user (CUSTOMER/OWNER - từ JWT token)
    """
    user_id: str
    role: Role

    @classmethod
    def from_jwt_payload(cls, payload: dict) -> "UserContext":
        """
        Create UserContext từ JWT payload.

        Args:
            payload: JWT decode payload

        Returns:
            UserContext instance

        Raises:
            ValueError: Nếu payload không hợp lệ
        """
        user_id = payload.get("sub")
        role_str = payload.get("role")

        if not user_id:
            raise ValueError("JWT payload missing 'sub' (user_id)")

        if not role_str:
            raise ValueError("JWT payload missing 'role'")

        # Parse role
        try:
            role = Role(role_str.upper())
        except ValueError:
            raise ValueError(f"Invalid role in JWT: {role_str}")

        return cls(user_id=user_id, role=role)

    @classmethod
    def from_auth_header(cls, db: Any, auth_header: str) -> "UserContext":
        """
        Create UserContext từ Authorization header.

        Args:
            db: Database session (để verify user exists)
            auth_header: "Bearer <token>"

        Returns:
            UserContext instance

        Raises:
            ValueError: Nếu token không hợp lệ hoặc user không tồn tại
        """
        from src.services.auth_service import AuthService

        if not auth_header.startswith("Bearer "):
            raise ValueError("Invalid authorization header format")

        token = auth_header[7:]  # Remove "Bearer "

        payload = AuthService.verify_token(token)
        if not payload:
            raise ValueError("Invalid or expired token")

        # Verify user exists
        from uuid import UUID
        user_uuid = UUID(payload["sub"])
        user = AuthService.get_user_by_id(db, user_uuid)
        if not user:
            raise ValueError("User not found")

        return cls.from_jwt_payload(payload)

    def to_guard_role(self) -> Role:
        """Convert sang Role enum"""
        return self.role

    def is_owner(self) -> bool:
        """Check if user is owner"""
        return self.role == Role.OWNER

    def is_customer(self) -> bool:
        """Check if user is customer"""
        return self.role == Role.CUSTOMER
