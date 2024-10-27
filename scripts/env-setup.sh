#!/bin/bash

# Script that sets enviroment up so Pycord doesn't fuck things up
# Author: @wh0crypt

if [[ ! -d "venv" || ! -d ".venv" ]]; then
  python3 -m venv ./venv
fi

source ./venv/bin/activate

if [[ $? -ne 0 ]]; then
  echo "Failed to activate the virtual environment."
  exit 1
fi

pip3 install git+https://github.com/Rapptz/discord-ext-menus
pip3 install py-cord==2.6.0
pip3 install -r requirements.txt

echo "Environment set up successfully and packages installed."
