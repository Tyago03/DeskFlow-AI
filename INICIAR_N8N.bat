@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where docker >nul 2>nul
if errorlevel 1 (echo Instale Docker Desktop primeiro. & pause & exit /b 1)
docker compose up -d
if errorlevel 1 (echo Falha ao iniciar n8n. & pause & exit /b 1)
echo n8n aberto em http://127.0.0.1:5678
start "" "http://127.0.0.1:5678"
pause
