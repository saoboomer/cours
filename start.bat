@echo off
cls
echo.
echo  ================================================
echo   PRONOTE Grade Analyzer - Demarrage rapide
echo  ================================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo  [X] ERREUR: Python non installe
        echo      Installez Python: https://www.python.org/
        timeout /t 5 >nul
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo  [OK] Python detecte: %PYTHON_CMD%

REM Quick dependency check (only check if flask is installed)
%PYTHON_CMD% -c "import flask" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo  [!] Installation des dependances...
    %PYTHON_CMD% -m pip install -q -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo  [X] Installation echouee
        echo      Lancez: INSTALL_DEPENDENCIES.bat
        timeout /t 5 >nul
        exit /b 1
    )
    echo  [OK] Dependances installees
) else (
    echo  [OK] Dependances presentes
)

echo.
echo  [*] Demarrage du backend...

REM Start backend in minimized window
cd backend
start /min "PRONOTE Backend" cmd /c "%PYTHON_CMD% app.py"

REM Quick wait for backend
timeout /t 2 /nobreak >nul

echo  [OK] Backend demarre (http://localhost:5000)
echo.
echo  [*] Ouverture du frontend...

cd ..\frontend
start "" index.html

timeout /t 1 /nobreak >nul

cls
echo.
echo  ================================================
echo   Application demarree avec succes!
echo  ================================================
echo.
echo   Backend:  http://localhost:5000
echo   Frontend: Ouvert dans votre navigateur
echo.
echo   Pour arreter le backend, fermez la fenetre
echo   "PRONOTE Backend" dans la barre des taches
echo.
echo  ================================================
echo.
echo  Appuyez sur une touche pour fermer...
pause >nul
