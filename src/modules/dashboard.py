# src/modules/dashboard.py
import streamlit as st
import pandas as pd
from database.models import Producto, Movimiento, Usuario
from database.session import get_db
from sqlalchemy import func  # ← AÑADIDO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io
from datetime import datetime

def dashboard():
    st.header("Dashboard Principal - StockSmart")
    st.markdown("---")

    # === MÉTRICAS PRINCIPALES ===
    col1, col2, col3, col4 = st.columns(4)
    
    with next(get_db()) as db:
        total_prod = db.query(Producto).count()
        bajo_stock = db.query(Producto).filter(Producto.stock < Producto.stock_min).count()
        
        # CORREGIDO: USAR func.sum()
        valor_inv = db.query(func.sum(Producto.precio * Producto.stock)).scalar() or 0
        
        movimientos_total = db.query(Movimiento).count()

        col1.metric("Productos Totales", total_prod)
        col2.metric("Stock Bajo", bajo_stock, 
                   delta=f"-{bajo_stock} alerta(s)" if bajo_stock else None)
        col3.metric("Valor del Inventario", f"${valor_inv:,.0f}")
        col4.metric("Movimientos Totales", movimientos_total)

    st.markdown("---")
    st.subheader("Kardex por Producto")

    # === OBTENER PRODUCTOS ===
    with next(get_db()) as db:
        productos = db.query(Producto).all()
        if not productos:
            st.warning("No hay productos registrados.")
            return

        opciones = {p.nombre: p for p in productos}
        prod_nombre = st.selectbox("Selecciona un producto:", list(opciones.keys()))

        selected = opciones[prod_nombre]
        
        # === OBTENER MOVIMIENTOS ===
        movimientos = db.query(Movimiento).filter(
            Movimiento.producto_id == selected.id
        ).order_by(Movimiento.fecha).all()

        if not movimientos:
            st.info(f"No hay movimientos registrados para **{prod_nombre}**.")
            return

        # === CALCULAR STOCK ACUMULADO ===
        data = []
        stock_acum = 0
        
        for m in movimientos:
            if m.cantidad > 0:
                stock_acum += m.cantidad
                tipo = "ENTRADA"
            else:
                stock_acum += m.cantidad
                tipo = "SALIDA"
            
            data.append({
                "Fecha": m.fecha.strftime("%Y-%m-%d %H:%M"),
                "Tipo": tipo,
                "Cantidad": abs(m.cantidad),
                "Motivo": m.motivo or "-",
                "Usuario": m.usuario.nombre if m.usuario else "Sistema",
                "Stock": stock_acum
            })

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        # === EXPORTAR A PDF ===
        if st.button("Exportar Kardex a PDF", key="export_pdf"):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch)
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=16,
                spaceAfter=30,
                alignment=1
            )
            elements.append(Paragraph(f"Kardex - {prod_nombre}", title_style))
            elements.append(Spacer(1, 12))

            table_data = [df.columns.tolist()] + df.values.tolist()
            table = Table(table_data, colWidths=[80, 60, 60, 80, 80, 60])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            elements.append(table)

            elements.append(Spacer(1, 20))
            elements.append(Paragraph(
                f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')} | StockSmart",
                styles['Normal']
            ))

            doc.build(elements)
            buffer.seek(0)
            
            st.success("PDF generado correctamente")
            st.download_button(
                label="Descargar Kardex PDF",
                data=buffer.getvalue(),
                file_name=f"kardex_{prod_nombre.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )