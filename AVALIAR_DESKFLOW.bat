@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (echo Execute INICIAR_DESKFLOW.bat primeiro. & pause & exit /b 1)
".venv\Scripts\python.exe" -m scripts.evaluate --mode ollama
set RESULT=%ERRORLEVEL%
if exist "evaluation\results" start "" "evaluation\results"
pause
exit /b %RESULT%
