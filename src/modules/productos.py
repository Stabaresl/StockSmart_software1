# src/modules/productos.py
import streamlit as st
import pandas as pd
from database.models import Producto
from database.session import get_db
from datetime import datetime

def gestionar_productos():
    st.header("Gestión de Productos")
    tab1, tab2, tab3, tab4 = st.tabs(["Registrar (CU-11)", "Editar/Eliminar (CU-12)", "Buscar (CU-13)", "Lista Completa"])

    # === REGISTRAR (CU-11) ===
    with tab1:
        with st.form("nuevo_producto"):
            nombre = st.text_input("Nombre del producto *", placeholder="Ej: Laptop Dell")
            categoria = st.text_input("Categoría", placeholder="Ej: Electrónicos")
            precio = st.number_input("Precio *", min_value=0.0, step=1000.0, format="%.0f")
            stock = st.number_input("Stock inicial", min_value=0, step=1, value=0)
            stock_min = st.number_input("Stock mínimo (alerta)", min_value=1, value=10)

            submitted = st.form_submit_button("Registrar Producto")
            if submitted:
                if not nombre.strip() or precio < 0:
                    st.error("Nombre y precio son obligatorios")
                else:
                    with next(get_db()) as db:
                        nuevo = Producto(
                            nombre=nombre.strip(),
                            categoria=categoria.strip() or None,
                            precio=precio,
                            stock=stock,
                            stock_min=stock_min
                        )
                        db.add(nuevo)
                        db.commit()
                        st.success(f"Producto '{nombre}' registrado con éxito")
                        st.rerun()

    # === EDITAR/ELIMINAR (CU-12) ===
    with tab2:
        with next(get_db()) as db:
            productos = db.query(Producto).all()
            if not productos:
                st.info("No hay productos registrados")
            else:
                opciones = {f"{p.id} - {p.nombre} ({p.categoria or 'Sin categoría'})": p for p in productos}
                seleccion = st.selectbox("Selecciona producto", options=opciones.keys(), key="edit_select")
                prod = opciones[seleccion]

                with st.form("edit_form"):
                    nuevo_nombre = st.text_input("Nombre", value=prod.nombre)
                    nuevo_categoria = st.text_input("Categoría", value=prod.categoria or "")
                    nuevo_precio = st.number_input("Precio", value=prod.precio, min_value=0.0)
                    nuevo_stock = st.number_input("Stock", value=prod.stock, min_value=0)
                    nuevo_stock_min = st.number_input("Stock mínimo", value=prod.stock_min, min_value=1)

                    col1, col2 = st.columns(2)
                    actualizar = col1.form_submit_button("Actualizar")
                    eliminar = col2.form_submit_button("Eliminar", type="primary")

                    if actualizar:
                        with next(get_db()) as db:
                            p = db.get(Producto, prod.id)
                            p.nombre = nuevo_nombre.strip()
                            p.categoria = nuevo_categoria.strip() or None
                            p.precio = nuevo_precio
                            p.stock = nuevo_stock
                            p.stock_min = nuevo_stock_min
                            db.commit()
                            st.success("Producto actualizado")
                            st.rerun()

                    if eliminar:
                        if st.session_state.get('confirm_delete') != prod.id:
                            st.session_state['confirm_delete'] = prod.id
                            st.warning(f"¿Seguro que deseas eliminar **{prod.nombre}**?")
                            if st.button("Confirmar eliminación", type="primary"):
                                with next(get_db()) as db:
                                    p = db.get(Producto, prod.id)
                                    db.delete(p)
                                    db.commit()
                                    del st.session_state['confirm_delete']
                                    st.success("Producto eliminado")
                                    st.rerun()
                        else:
                            del st.session_state['confirm_delete']

    # === BUSCAR (CU-13) ===
    with tab3:
        busqueda = st.text_input("Buscar por nombre o categoría", key="search_input")
        if busqueda:
            with next(get_db()) as db:
                resultados = db.query(Producto).filter(
                    (Producto.nombre.ilike(f"%{busqueda}%")) |
                    (Producto.categoria.ilike(f"%{busqueda}%"))
                ).all()
                if resultados:
                    df = pd.DataFrame([{
                        "ID": p.id,
                        "Nombre": p.nombre,
                        "Categoría": p.categoria or "-",
                        "Precio": f"${p.precio:,.0f}",
                        "Stock": p.stock,
                        "Mínimo": p.stock_min,
                        "Estado": "BAJO" if p.stock < p.stock_min else "OK"
                    } for p in resultados])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No se encontraron productos")

    # === LISTA COMPLETA ===
    with tab4:
        with next(get_db()) as db:
            productos = db.query(Producto).all()
            if productos:
                df = pd.DataFrame([{
                    "ID": p.id,
                    "Nombre": p.nombre,
                    "Categoría": p.categoria or "-",
                    "Precio": f"${p.precio:,.0f}",
                    "Stock": p.stock,
                    "Mínimo": p.stock_min,
                    "Estado": "BAJO" if p.stock < p.stock_min else "OK"
                } for p in productos])
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Exportar CSV",
                    data=csv,
                    file_name=f"productos_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No hay productos registrados")