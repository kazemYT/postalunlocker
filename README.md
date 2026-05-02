# postal unlocker

simple tool for editing postal plus save file and unlocking levels

## what it does

- unlock / lock all levels
- toggle individual levels
- toggle kid mode
- toggle debug info
- auto-detects `POSTAL.INI` in appdata
- saves last used path

## requirements

- python 3.10+
- windows (uses appdata paths)
- rich library

install deps:
pip install rich

# how to use

run python main.py

on first launch it will try to find POSTAL.INI automatically
if not found, ask you to enter path manually
save path for next runs

inside program:

all - unlock all levels
lockall - lock all levels
kidmode - toggle kid mode
debug - toggle debug info
1-22 - toggle specific level
q - quit

# FAQ

ini not found - game must be launched at least once or path is wrong

changes not saving - try running terminal as administrator

game crashes -restore original POSTAL.INI backup

# notes

this tool edits local config files only
no game files are modified

use at your own risk
