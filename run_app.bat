@echo off

cd /d "%~dp0"

call .venv\Scripts\activate

start "FastAPI Backend" cmd /k "uvicorn app.main:app --reload"

timeout /t 2 /nobreak >nul

start "Streamlit Frontend" cmd /k "streamlit run frontend\streamlit_app.py"