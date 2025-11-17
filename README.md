# StockSmart - Incremento 1

## Descripción
Aplicación web para gestión de inventario. Este incremento implementa:
- Autenticación segura con roles
- CRUD completo de productos
- Búsqueda y exportación

## Casos de Uso Implementados
| ID | Nombre | Estado |
|----|------|--------|
| CU-01 | Iniciar Sesión | Completed |
| CU-03 | Recuperar Contraseña | Completed (simulada) |
| CU-04 | Cambiar Contraseña | Completed |
| CU-06 | Registrar Usuario | Completed (solo admin) |
| CU-11 | Registrar Producto | Completed |
| CU-12 | Modificar/Eliminar Producto | Completed |
| CU-13 | Buscar Productos | Completed |
| CU-18 | Cerrar Sesión | Completed |

## Instalación
```bash
pip install -r requirements.txt
streamlit run src/main.py