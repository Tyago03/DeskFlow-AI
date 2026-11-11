@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 where py >nul 2>nul && (py -3 -m venv .venv) || (python -m venv .venv)
)
if not exist ".venv\Scripts\python.exe" (
 echo Falha: instale Python 3.11 ou superior.
 pause & exit /b 1
)
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt
if errorlevel 1 (echo Falha ao instalar dependencias. & pause & exit /b 1)
echo Iniciando DeskFlow AI local. Para encerrar, pressione Ctrl+C.
".venv\Scripts\python.exe" -m app.launch
pause
