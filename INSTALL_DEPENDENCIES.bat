@echo off
echo ========================================
echo Installation des dependances
echo ========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ERREUR: Python n'est pas installe
        echo Telechargez Python depuis: https://www.python.org/downloads/
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo Python trouve: %PYTHON_CMD%
echo.

echo Mise a jour de pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo.
echo Installation des packages...
echo Cela peut prendre plusieurs minutes...
echo.

%PYTHON_CMD% -m pip install pronotepy
%PYTHON_CMD% -m pip install flask
%PYTHON_CMD% -m pip install flask-cors
%PYTHON_CMD% -m pip install numpy
%PYTHON_CMD% -m pip install pandas
%PYTHON_CMD% -m pip install scipy
%PYTHON_CMD% -m pip install python-dotenv

echo.
echo ========================================
echo Installation terminee!
echo ========================================
echo.
echo Vous pouvez maintenant lancer start.bat
echo.
pause
