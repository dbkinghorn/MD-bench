#!/usr/bin/env bash

# PyInstaller build command for namd-gpu
#./venv/bin/pyinstaller --clean \
pyinstaller --clean \
    --distpath='./dist' \
    --workpath='./build' \
    --specpath='.' \
    --onefile \
     ./namd_gpu.spec
