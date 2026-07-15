@echo off
title Lanzar CyberDownloader
:: Ejecuta la app usando pythonw.exe del venv para no abrir ventanas de consola negras feas de fondo
start "" "%~dp0venv\Scripts\pythonw.exe" "%~dp0main.py"
exit
