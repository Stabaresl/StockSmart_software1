# src/database/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100))
    email = Column(String(100), unique=True)
    password_hash = Column(String(255))
    google_id = Column(String(100), unique=True)
    rol = Column(String(20), default="empleado")
    activo = Column(Boolean, default=True)  # ← AHORA FUNCIONA

class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    categoria = Column(String(50))
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    stock_min = Column(Integer, default=10)

class Movimiento(Base):
    __tablename__ = 'movimientos'
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'))
    tipo = Column(String(20))
    cantidad = Column(Integer)
    motivo = Column(String(200))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    fecha = Column(DateTime, default=datetime.utcnow)
    
    producto = relationship("Producto")
    usuario = relationship("Usuario")