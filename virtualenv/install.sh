#!/bin/bash
#
# Installation of the Python environment for workers and appserver.
#
# Assuming ~khresmoi/virtualenv as the target directory, 
# and Ubuntu (tested on 10.04) with sudo possibility 
# or python-dev package installed.

cd ~khresmoi

# Check if we have python-dev installed
dpkg -s python-dev || sudo apt-get install python-dev

# Download virtualenv
wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py

# Install virtualenv 
mkdir virtualenv
python virtualenv.py virtualenv

# Activate virtualenv and install needed libraries
source virtualenv/bin/activate
pip install flask validictory regex

# clean up
rm virtualenv virtualenv.py
