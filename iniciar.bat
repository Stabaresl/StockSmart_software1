@echo off
cd /d "%~dp0"
echo.
echo ========================================
echo   INICIANDO STOCKSMART...
echo ========================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado.
    echo Descarga: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Crear entorno virtual
if not exist venv (
    echo Creando entorno virtual...
    python -m venv venv
)

:: Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

:: Forzar instalacion de dependencias
echo Instalando dependencias (streamlit, sqlalchemy, etc.)...
pip install -r requirements.txt --quiet --no-cache-dir

:: Configurar PYTHONPATH
set PYTHONPATH=%CD%

:: Ejecutar con python -m streamlit (100% seguro)
echo.
echo ========================================
echo   APP CORRIENDO EN: http://localhost:8501
echo ========================================
echo.
python -m streamlit run src/main.py

pause