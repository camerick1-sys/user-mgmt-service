import bcrypt

def hash_password(raw: str) -> str:
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")

def verify_password(raw: str, hashed: str) -> bool:
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return bcrypt.checkpw(raw, hashed.encode("utf-8"))
