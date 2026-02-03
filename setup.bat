@echo off
echo Virtual Enviorment
python -m venv .venv
echo Installing
call .venv\Scripts\activate.bat
pip install -e .
echo Done
cmd /k
