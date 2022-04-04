#!/usr/bin/env bash

# PyInstaller build command for namd-cpu
#./venv/bin/pyinstaller --clean \
pyinstaller --clean \
    --distpath='./dist' \
    --workpath='./build' \
    --specpath='.' \
    --onefile \
     ./namd-cpu.spec
