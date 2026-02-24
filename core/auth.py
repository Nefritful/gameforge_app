import hashlib
from typing import Optional, Dict, Any
from .db import db_one, db_exec

def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    return db_one("SELECT id, email, password_hash FROM gf_users WHERE email=%s", (email,))

def verify_login(email: str, password: str) -> Optional[Dict[str, Any]]:
    u = get_user_by_email(email)
    if not u:
        return None
    if u["password_hash"] != sha256_hex(password):
        return None
    return {"id": u["id"], "email": u["email"]}

def register_user(email: str, password: str) -> Dict[str, Any]:
    # минимальная защита: уникальность email обеспечена БД
    pwd = sha256_hex(password)
    user_id = db_exec("INSERT INTO gf_users(email, password_hash) VALUES (%s,%s)", (email, pwd))
    return {"id": user_id, "email": email}
