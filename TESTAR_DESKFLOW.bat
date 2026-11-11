@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo Execute INICIAR_DESKFLOW.bat primeiro. & pause & exit /b 1)
".venv\Scripts\python.exe" -m pip install -q -r requirements-dev.txt
".venv\Scripts\python.exe" -m pytest -q
set RESULT=%ERRORLEVEL%
if %RESULT% NEQ 0 (echo Falhas detectadas. Verifique o resumo.) else (echo Testes concluidos sem falhas.)
pause
exit /b %RESULT%
