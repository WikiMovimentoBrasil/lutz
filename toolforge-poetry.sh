#!/usr/bin/env bash

if [ ! -d "$HOME/www/python/venv" ]; then
    python3 -m venv "$HOME/www/python/venv"
fi
source "$HOME/www/python/venv/bin/activate"
pip install --upgrade pip setuptools
pip install poetry
