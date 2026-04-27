"""Autenticação simples para o MVP."""

from passlib.context import CryptContext

from modules.database import execute, rows

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def ensure_default_admin() -> None:
    if rows("SELECT id FROM users LIMIT 1"):
        return
    execute(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'admin')",
        ("Administrador", "admin@empresa.com", pwd_context.hash("admin123")),
    )


def authenticate(email: str, password: str) -> bool:
    user = rows("SELECT * FROM users WHERE email = ?", (email,))
    if not user:
        return False
    return pwd_context.verify(password, user[0]["password_hash"])
