@echo off
echo ========================================
echo Test de connexion au backend
echo ========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ERREUR: Python non trouve
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo Demarrage du serveur backend...
echo.

cd backend
%PYTHON_CMD% app.py

pause
