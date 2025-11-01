#!/bin/bash
# Vercel用のビルドスクリプト

# Python3とpip3を使用
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium

