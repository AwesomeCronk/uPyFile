@echo OFF
echo installing uPyFile to %1
echo.
echo.
pyinstaller uPyFile.py
del uPyFile.spec
rmdir /s /q build
move dist\uPyFile %1\
rmdir dist
echo done.