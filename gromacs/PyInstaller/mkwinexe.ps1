#!/usr/bin/env bash

# PyInstaller build command for PugetBench-Numeric
C:\Users\don\miniconda3\envs\dev-base\Scripts\pyinstaller --clean `
    --console `
    --distpath='./dist' `
    --workpath='./build' `
    --specpath='.' `
    --onefile `
    ./pugetbench-numeric.spec

#    ..\pugetbench-numeric.py
