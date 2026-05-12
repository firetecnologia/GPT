"""Autenticação simples para o MVP."""

from passlib.context import CryptContext

from modules.database import execute, rows

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def ensure_default_admin() -> None:
    if rows("SELECT id FROM users LIMIT 1"):
        return
    execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
        ("Administrador", "firetecnologia@gmail.com", pwd_context.hash("1234")),
    )


def authenticate(email: str, password: str) -> bool:
    user = rows("SELECT * FROM users WHERE email = ?", (email,))
    if not user:
        return False
    return pwd_context.verify(password, user[0]["password_hash"])



def create_user(name: str, email: str, password: str, role: str = "user") -> None:
    execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (name, email, pwd_context.hash(password), role),
    )


def list_users() -> list[dict]:
    return rows("SELECT id, name, email, role, created_at FROM users ORDER BY id DESC")
