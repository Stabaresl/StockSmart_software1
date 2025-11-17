# src/modules/auth.py
import streamlit as st
import bcrypt
from database.models import Usuario
from database.session import get_db
from utils.validators import validate_email, validate_password
from services.google_auth import get_flow, get_user_info
import secrets

# === HASH Y CHECK ===
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# === LOGIN NORMAL (CU-01) ===
def login():
    if 'user' in st.session_state:
        return st.session_state['user']
    
    st.header("Iniciar Sesión")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Con Email")
        email = st.text_input("Email", key="email_login")
        password = st.text_input("Contraseña", type="password", key="pass_login")  # CORREGIDO: solo un key
        
        if st.button("Iniciar Sesión", key="btn_email"):
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
    
    with col2:
        st.subheader("Con Google (CU-02)")
        if st.button("Autenticar con Google", key="btn_google"):
            try:
                flow = get_flow()
                auth_url, _ = flow.authorization_url(prompt='consent')
                st.session_state['google_auth_url'] = auth_url
                st.rerun()
            except Exception as e:
                st.error(f"Error al iniciar Google: {e}")

    # Redirección automática a Google
    if 'google_auth_url' in st.session_state:
        st.markdown(
            f'<meta http-equiv="refresh" content="0; url={st.session_state["google_auth_url"]}">',
            unsafe_allow_html=True
        )

    return None

# === CALLBACK DE GOOGLE ===
def handle_google_callback():
    if 'code' in st.query_params:
        try:
            flow = get_flow()
            flow.fetch_token(authorization_response=st.experimental_get_query_params())
            creds = flow.credentials
            user_info = get_user_info(creds)
            
            email = user_info['email']
            nombre = user_info.get('name', email.split('@')[0])
            google_id = user_info['id']
            
            for db in get_db():
                user = db.query(Usuario).filter(Usuario.email == email).first()
                if not user:
                    user = Usuario(
                        nombre=nombre,
                        email=email,
                        google_id=google_id,
                        rol="empleado",
                        activo=True
                    )
                    db.add(user)
                    db.commit()
                else:
                    user.google_id = google_id
                    db.commit()
                
                st.session_state['user'] = {
                    'id': user.id,
                    'nombre': user.nombre,
                    'email': user.email,
                    'rol': user.rol
                }
            st.success(f"Bienvenido con Google, {nombre}")
            st.rerun()
        except Exception as e:
            st.error(f"Error en autenticación con Google: {e}")

# === LOGOUT ===
def logout():
    if st.sidebar.button("Cerrar Sesión (CU-18)"):
        st.session_state.pop('user', None)
        st.rerun()

# === REQUERIR LOGIN ===
def require_login():
    if 'user' not in st.session_state:
        st.warning("Debes iniciar sesión para continuar.")
        login()
        st.stop()

# === REGISTRAR USUARIO (CU-06) ===
def register_user():
    st.header("Registrar Usuario (CU-06) - Solo Admin")
    require_login()
    if st.session_state['user']['rol'] != 'admin':
        st.error("Acceso denegado: Solo administradores")
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
                        user = Usuario(
                            nombre=nombre,
                            email=email,
                            password_hash=hashed,
                            rol=rol,
                            activo=activo
                        )
                        db.add(user)
                        db.commit()
                        st.success("Usuario registrado exitosamente")
                        st.rerun()

# === CAMBIAR CONTRASEÑA (CU-04) ===
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
                st.error("Contraseña debe tener al menos 8 caracteres, letras y números")
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

# === RECUPERAR CONTRASEÑA (CU-03) ===
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
                    st.success(f"Simulación: Enlace enviado a {email}")
                    st.code(f"Token: {token}")
                    st.info("En producción, se enviaría por correo con smtplib.")
                else:
                    st.error("Email no registrado")