# src/utils/seeders.py
from database.models import Usuario, Producto, Movimiento
from database.session import get_db
from utils.validators import hash_password
import random
from datetime import datetime, timedelta

def run_seeders():
    with next(get_db()) as db:
        # === ADMIN ===
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

        # === EMPLEADO DE PRUEBA ===
        if not db.query(Usuario).filter(Usuario.email == "empleado@stocksmart.com").first():
            emp = Usuario(
                nombre="Empleado Prueba",
                email="empleado@stocksmart.com",
                password_hash=hash_password("emp123"),
                rol="empleado",
                activo=True
            )
            db.add(emp)
            db.commit()

        # === PRODUCTOS ===
        productos_data = [
            ("Laptop Dell", "Electrónicos", 2500000, 5, 3),
            ("Mouse Logitech", "Accesorios", 45000, 20, 5),
            ("Teclado Mecánico", "Accesorios", 180000, 8, 2),
            ("Monitor 24\"", "Electrónicos", 850000, 3, 1),
        ]
        
        productos_creados = []
        for nombre, cat, precio, stock, min_stock in productos_data:
            if not db.query(Producto).filter(Producto.nombre == nombre).first():
                p = Producto(
                    nombre=nombre,
                    categoria=cat,
                    precio=precio,
                    stock=stock,
                    stock_min=min_stock
                )
                db.add(p)
                db.flush()
                productos_creados.append(p)
        db.commit()

        # === MOVIMIENTOS: SOLO LA PRIMERA VEZ ===
        if productos_creados and not db.query(Movimiento).first():
            usuarios = db.query(Usuario).all()
            motivos = ["Compra", "Venta", "Devolución", "Ajuste"]
            now = datetime.utcnow()
            
            for p in productos_creados:
                for i in range(random.randint(3, 7)):
                    tipo = random.choice(["entrada", "salida"])
                    cant = random.randint(1, 5)
                    
                    # Evitar salidas sin stock
                    if tipo == "salida":
                        stock_actual = db.query(Producto).get(p.id).stock
                        if stock_actual < cant:
                            continue
                    
                    mov = Movimiento(
                        producto_id=p.id,
                        tipo=tipo,
                        cantidad=cant if tipo == "entrada" else -cant,
                        motivo=random.choice(motivos),
                        usuario_id=random.choice([u.id for u in usuarios]),
                        fecha=now - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
                    )
                    db.add(mov)
                    
                    # ACTUALIZAR STOCK
                    producto = db.query(Producto).get(p.id)
                    producto.stock += cant if tipo == "entrada" else -cant
            db.commit()