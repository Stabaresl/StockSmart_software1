# src/main.py
import streamlit as st
from database.session import get_db  # ABSOLUTA
from database.models import Usuario  # ABSOLUTA
from modules.auth import login, logout, require_login, register_user, change_password, recover_password
from modules.productos import gestionar_productos
from utils.validators import hash_password  # ABSOLUTA

st.set_page_config(page_title="StockSmart", layout="wide", page_icon="chart_with_upwards_trend")

# === CREAR ADMIN POR DEFECTO ===
with next(get_db()) as db:
    if not db.query(Usuario).filter(Usuario.email == "admin@stocksmart.com").first():
        admin = Usuario(
            nombre="Administrador",
            email="admin@stocksmart.com",
            password_hash=hash_password("admin123"),
            rol="admin",
            activo=True
        )
        db.add(admin)
        db.commit()

# === SIDEBAR ===
if 'user' not in st.session_state:
    login()
else:
    st.sidebar.success(f"**{st.session_state['user']['nombre']}** ({st.session_state['user']['rol']})")
    logout()

    menu = ["Dashboard", "Productos", "Cambiar Contraseña"]
    if st.session_state['user']['rol'] == 'admin':
        menu.insert(1, "Registrar Usuario")

    opcion = st.sidebar.selectbox("Menú", menu)

    require_login()

    if opcion == "Dashboard":
        st.title("StockSmart - Panel Principal")
        st.write("Sistema de gestión de inventario para PYMES")
        
    elif opcion == "Productos":
        gestionar_productos()

    elif opcion == "Cambiar Contraseña":
        change_password()

    elif opcion == "Registrar Usuario":
        register_user()