# src/modules/productos.py
import streamlit as st
import pandas as pd
from database.models import Producto  # ABSOLUTA
from database.session import get_db  # ABSOLUTA

def gestionar_productos():
    st.header("Gestión de Productos")
    tab1, tab2, tab3, tab4 = st.tabs(["Registrar (CU-11)", "Editar/Eliminar (CU-12)", "Buscar (CU-13)", "Lista Completa"])

    # === REGISTRAR ===
    with tab1:
        with st.form("nuevo_producto"):
            nombre = st.text_input("Nombre del producto")
            categoria = st.text_input("Categoría")
            precio = st.number_input("Precio", min_value=0.0, step=0.01)
            stock = st.number_input("Stock inicial", min_value=0, step=1)
            stock_min = st.number_input("Stock mínimo (alerta)", min_value=1, value=10)

            if st.form_submit_button("Registrar Producto"):
                if not nombre or precio < 0:
                    st.error("Nombre y precio son obligatorios")
                else:
                    for db in get_db():
                        prod = Producto(nombre=nombre, categoria=categoria, precio=precio, stock=stock, stock_min=stock_min)
                        db.add(prod)
                        db.commit()
                        st.success(f"Producto '{nombre}' registrado")
                        st.rerun()

    # === EDITAR/ELIMINAR ===
    with tab2:
        for db in get_db():
            productos = db.query(Producto).all()
            if not productos:
                st.info("No hay productos registrados")
            else:
                seleccion = st.selectbox(
                    "Selecciona producto",
                    options=[f"{p.id} - {p.nombre} ({p.categoria or 'Sin categoría'})" for p in productos],
                    key="edit_select"
                )
                if seleccion:
                    pid = int(seleccion.split(" - ")[0])
                    prod = db.query(Producto).get(pid)

                    with st.form("edit_form"):
                        prod.nombre = st.text_input("Nombre", value=prod.nombre)
                        prod.categoria = st.text_input("Categoría", value=prod.categoria or "")
                        prod.precio = st.number_input("Precio", value=prod.precio, min_value=0.0)
                        prod.stock = st.number_input("Stock", value=prod.stock, min_value=0)
                        prod.stock_min = st.number_input("Stock mínimo", value=prod.stock_min, min_value=1)

                        col1, col2 = st.columns(2)
                        if col1.form_submit_button("Actualizar"):
                            db.commit()
                            st.success("Producto actualizado")
                            st.rerun()
                        if col2.form_submit_button("Eliminar", type="primary"):
                            db.delete(prod)
                            db.commit()
                            st.success("Producto eliminado")
                            st.rerun()

    # === BUSCAR ===
    with tab3:
        busqueda = st.text_input("Buscar por nombre o categoría")
        if busqueda:
            for db in get_db():
                resultados = db.query(Producto).filter(
                    (Producto.nombre.ilike(f"%{busqueda}%")) |
                    (Producto.categoria.ilike(f"%{busqueda}%"))
                ).all()
                if resultados:
                    df = pd.DataFrame([{
                        "ID": p.id,
                        "Nombre": p.nombre,
                        "Categoría": p.categoria or "-",
                        "Precio": f"${p.precio:.2f}",
                        "Stock": p.stock,
                        "Mínimo": p.stock_min
                    } for p in resultados])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No se encontraron productos")

    # === LISTA COMPLETA ===
    with tab4:
        for db in get_db():
            productos = db.query(Producto).all()
            if productos:
                df = pd.DataFrame([{
                    "ID": p.id,
                    "Nombre": p.nombre,
                    "Categoría": p.categoria or "-",
                    "Precio": f"${p.precio:.2f}",
                    "Stock": p.stock,
                    "Mínimo": p.stock_min,
                    "Estado": "BAJO" if p.stock < p.stock_min else "OK"
                } for p in productos])
                st.dataframe(df, use_container_width=True)
                st.download_button("Exportar CSV", df.to_csv(index=False), "productos.csv", "text/csv")
            else:
                st.info("No hay productos")