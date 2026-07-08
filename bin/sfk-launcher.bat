@echo off
REM SFK Launcher — double-click entry point (Windows)
setlocal
set "DIR=%~dp0"

where pythonw >nul 2>nul
if %ERRORLEVEL%==0 (
    start "" pythonw "%DIR%sfk_gui.py"
    goto :eof
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    start "" python "%DIR%sfk_gui.py"
    goto :eof
)

echo ERRO: Python nao encontrado no PATH. Instale o Python 3 e tente de novo.
pause
