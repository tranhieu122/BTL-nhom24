"""User management business logic."""
from __future__ import annotations
from dao.user_dao import UserDAO
from models.user import User
from utils.password_hash import hash_password
from utils.validators import is_valid_email, is_valid_phone
from utils.logger import get_logger

_log = get_logger(__name__)


class UserController:
    def __init__(self) -> None:
        self.user_dao = UserDAO()

    def list_users(self, keyword: str = "") -> list[User]:
        users = self.user_dao.list_all()
        kw = keyword.strip().lower()
        if not kw:
            return users
        return [u for u in users if kw in u.username.lower()
                or kw in u.full_name.lower() or kw in u.role.lower()]

    def save_user(self, payload: dict[str, str]) -> User:
        user_id   = payload["user_id"].strip().upper()
        username  = payload["username"].strip()
        full_name = payload["full_name"].strip()
        email     = payload["email"].strip()
        phone     = payload["phone"].strip()

        if not user_id:
            raise ValueError("Ma nguoi dung khong duoc de trong.")
        if not username or len(username) < 3:
            raise ValueError("Ten dang nhap phai co it nhat 3 ky tu.")
        if not full_name:
            raise ValueError("Ho va ten khong duoc de trong.")
        if not is_valid_email(email):
            raise ValueError("Email khong hop le.")
        if not is_valid_phone(phone):
            raise ValueError("So dien thoai khong hop le.")

        existing = self.user_dao.find_by_id(user_id)
        is_new = existing is None

        # Duplicate username check (only for new users or username change)
        by_username = self.user_dao.find_by_username(username)
        if by_username is not None and by_username.user_id != user_id:
            raise ValueError(f"Ten dang nhap '{username}' da duoc su dung.")

        # Duplicate email check
        by_email = self.user_dao.find_by_email(email)
        if by_email is not None and by_email.user_id != user_id:
            raise ValueError("Email nay da duoc dang ky boi nguoi dung khac.")

        password = payload.get("password", "").strip()
        if password:
            password_hash = hash_password(password)
        elif not is_new:
            password_hash = existing.password_hash  # type: ignore[union-attr]
        else:
            raise ValueError("Mat khau khong duoc de trong khi them moi.")

        user = User(
            user_id=user_id,
            username=username,
            full_name=full_name,
            role=payload["role"].strip(),
            email=email, phone=phone,
            password_hash=password_hash,
            status=payload["status"].strip(),
        )
        return self.user_dao.save(user)

    def delete_user(self, user_id: str) -> None:
        self.user_dao.delete(user_id)
