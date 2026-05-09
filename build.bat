@echo off
echo Compiling AutoLapse...
call .\.venv\Scripts\activate.bat
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "AutoLapse" "src/main.py"
echo Done! Executable is in the dist folder.
pause
