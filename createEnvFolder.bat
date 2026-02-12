@echo off
set PROJECT_NAME=ness_automation_project

echo Creating project structure: %PROJECT_NAME%
echo.

REM Create main project folder
REM mkdir %PROJECT_NAME%
REM cd %PROJECT_NAME%

REM Create directories
mkdir data
mkdir pages
mkdir tests
mkdir utils

REM Create files
type nul > conftest.py
type nul > pytest.ini
type nul > .gitignore
type nul > requirements.txt

echo.
echo Project structure created successfully.
echo.
pause
