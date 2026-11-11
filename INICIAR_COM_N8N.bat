@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo Execute INICIAR_DESKFLOW.bat primeiro. & pause & exit /b 1)
set "DESKFLOW_ALLOW_DOCKER=1"
echo AVISO: para integrar com n8n Docker, o backend escutara em todas as interfaces.
echo Restrinja o firewall local e NAO exponha a porta 8000 na internet.
".venv\Scripts\python.exe" -m app.launch
pause
