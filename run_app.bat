@echo off
title Student Expense Tracker - TU Dublin
cd /d "%~dp0"
echo ===================================================
echo   Launching Student Expense Tracker (TU Dublin)
echo ===================================================
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while launching the application.
    pause
)
