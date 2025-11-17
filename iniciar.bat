@echo off
cd /d "%~dp0"
echo INICIANDO STOCKSMART...

if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat
set PYTHONPATH=%CD%
pip install -r requirements.txt --quiet

echo.
echo App corriendo en: http://localhost:8501
echo.
streamlit run src/main.py

pause