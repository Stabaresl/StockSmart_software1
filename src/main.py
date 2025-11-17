# src/main.py
import streamlit as st
from database.session import get_db
from database.models import Usuario
from modules.auth import (
    login, logout, handle_google_callback,
    register_user, change_password
)
from modules.productos import gestionar_productos
from modules.dashboard import dashboard
from utils.seeders import run_seeders

# === CONFIGURACIÓN ===
st.set_page_config(
    page_title="StockSmart",
    layout="wide",
    page_icon="store",
    initial_sidebar_state="expanded"
)

# === CALLBACK DE GOOGLE (CU-02) ===
handle_google_callback()

# === SEEDERS: EJECUTAR UNA SOLA VEZ ===
if 'seeders_ejecutados' not in st.session_state:
    with next(get_db()) as db:
        run_seeders()
    st.session_state['seeders_ejecutados'] = True
    st.success("Base de datos inicializada con datos de prueba")

# === INICIO DE SESIÓN ===
if 'user' not in st.session_state:
    # === PANTALLA DE LOGIN ===
    st.title("StockSmart - Sistema de Inventario")
    st.markdown("### Inicia sesión para continuar")
    login()
else:
    # === SESIÓN ACTIVA ===
    user = st.session_state['user']
    
    # === SIDEBAR ===
    with st.sidebar:
        st.success(f"**{user['nombre']}**")
        st.info(f"Rol: **{user['rol']}**")
        st.markdown("---")
        logout()

        # === MENÚ PRINCIPAL ===
        menu = ["Dashboard", "Productos", "Cambiar Contraseña"]
        if user['rol'] == 'admin':
            menu.insert(1, "Registrar Usuario")

        opcion = st.selectbox("Navegación", menu, key="main_menu")

    # === CONTENIDO ===
    if opcion == "Dashboard":
        dashboard()
    elif opcion == "Productos":
        gestionar_productos()
    elif opcion == "Cambiar Contraseña":
        change_password()
    elif opcion == "Registrar Usuario":
        register_user()