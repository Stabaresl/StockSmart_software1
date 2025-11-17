# src/modules/auth.py
import streamlit as st
import bcrypt
from database.models import Usuario  # ABSOLUTA
from database.session import get_db  # ABSOLUTA
from utils.validators import validate_email, validate_password  # ABSOLUTA
import secrets

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login():
    if 'user' in st.session_state:
        return st.session_state['user']
    
    st.header("Iniciar Sesión (CU-01)")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Iniciar Sesión"):
        for db in get_db():
            user = db.query(Usuario).filter(Usuario.email == email).first()
            if user and user.activo and check_password(password, user.password_hash):
                st.session_state['user'] = {
                    'id': user.id,
                    'nombre': user.nombre,
                    'email': user.email,
                    'rol': user.rol
                }
                st.success(f"Bienvenido, {user.nombre}")
                st.rerun()
            else:
                st.error("Credenciales incorrectas o cuenta inactiva")
    return None

def logout():
    if st.sidebar.button("Cerrar Sesión (CU-18)"):
        st.session_state.pop('user', None)
        st.rerun()

def require_login():
    if 'user' not in st.session_state:
        st.warning("Debes iniciar sesión para continuar.")
        login()
        st.stop()

def register_user():
    st.header("Registrar Usuario (CU-06) - Solo Admin")
    require_login()
    if st.session_state['user']['rol'] != 'admin':
        st.error("Acceso denegado")
        return

    with st.form("register_form"):
        nombre = st.text_input("Nombre completo")
        email = st.text_input("Email")
        password = st.text_input("Contraseña", type="password")
        rol = st.selectbox("Rol", ["empleado", "admin"])
        activo = st.checkbox("Cuenta activa", value=True)

        if st.form_submit_button("Registrar"):
            if not all([nombre, email, password]):
                st.error("Todos los campos son obligatorios")
            elif not validate_email(email):
                st.error("Email inválido")
            elif not validate_password(password):
                st.error("Contraseña debe tener al menos 8 caracteres, letras y números")
            else:
                for db in get_db():
                    if db.query(Usuario).filter(Usuario.email == email).first():
                        st.error("Email ya registrado")
                    else:
                        hashed = hash_password(password)
                        user = Usuario(nombre=nombre, email=email, password_hash=hashed, rol=rol, activo=activo)
                        db.add(user)
                        db.commit()
                        st.success("Usuario registrado exitosamente")
                        st.rerun()

def change_password():
    st.header("Cambiar Contraseña (CU-04)")
    require_login()
    user_id = st.session_state['user']['id']

    with st.form("change_pass"):
        current = st.text_input("Contraseña actual", type="password")
        new_pass = st.text_input("Nueva contraseña", type="password")
        confirm = st.text_input("Confirmar nueva contraseña", type="password")

        if st.form_submit_button("Cambiar"):
            if not all([current, new_pass, confirm]):
                st.error("Todos los campos son obligatorios")
            elif new_pass != confirm:
                st.error("Las contraseñas no coinciden")
            elif not validate_password(new_pass):
                st.error("Contraseña débil")
            else:
                for db in get_db():
                    user = db.query(Usuario).get(user_id)
                    if check_password(current, user.password_hash):
                        user.password_hash = hash_password(new_pass)
                        db.commit()
                        st.success("Contraseña actualizada")
                        st.rerun()
                    else:
                        st.error("Contraseña actual incorrecta")

def recover_password():
    st.header("Recuperar Contraseña (CU-03)")
    email = st.text_input("Ingresa tu email registrado")
    
    if st.button("Enviar enlace de recuperación"):
        if not validate_email(email):
            st.error("Email inválido")
        else:
            for db in get_db():
                user = db.query(Usuario).filter(Usuario.email == email).first()
                if user:
                    token = secrets.token_hex(16)
                    st.success(f"Simulación: Enlace enviado a {email}\nToken: `{token}`")
                    st.info("En producción, se enviaría por correo con smtplib.")
                else:
                    st.error("Email no registrado")