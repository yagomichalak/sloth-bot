@echo off
rem Script that sets up the environment so Pycord doesn't fuck things up
rem Author: @wh0crypt

if not exist "venv\" (
  python -m venv venv
)

call venv\Scripts\activate.bat

if errorlevel 1 (
  echo Failed to activate the virtual environment.
  exit /b 1
)

pip install git+https://github.com/Rapptz/discord-ext-menus
pip install py-cord==2.6.0
pip install -r requirements.txt

echo Environment set up successfully and packages installed.
