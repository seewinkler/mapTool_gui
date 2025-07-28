@echo off

REM in das Verzeichnis wechseln, in dem die .bat liegt
pushd "%~dp0"  

REM Python-Skript aufrufen (oder py -3 für den Windows Python-Launcher)
py main.py  

REM warten, bis eine Taste gedrückt wird
pause  

REM zum Vorherigen Verzeichnis zurückkehren
popd