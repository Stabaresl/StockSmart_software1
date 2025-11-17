# src/utils/validators.py
import re
import bcrypt

def validate_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    """Valida que la contraseña tenga al menos 8 caracteres, letras y números"""
    return len(password) >= 8 and any(c.isdigit() for c in password) and any(c.isalpha() for c in password)

def hash_password(password: str) -> str:
    """Genera hash seguro de la contraseña"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))