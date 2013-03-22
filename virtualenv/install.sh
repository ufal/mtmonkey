#!/bin/bash
#
# Installation of mt-worker environment.
#
# Download virtualenv
wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py

# Install virtualenv 
mkdir virtualenv
python virtualenv.py virtualenv

# Activate virtualenv and install needed libraries
source virtualenv/bin/activate
pip install flask validictory regex
