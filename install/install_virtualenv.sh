#!/bin/bash
#
# Installation of the Python environment for workers and appserver.
#
# Assuming ~$USER/virtualenv as the target directory, 
# and Ubuntu (tested on 10.04) with sudo possibility 
# or python-dev package installed.

if [ -z $SHARE -o -z $USER ]; then
    print "Usage: USER=khresmoi SHARE=/mnt/share install_virtualenv.sh"
    exit 1
fi

cd ~$USER

# Check if we have python-dev installed
dpkg -s python-dev || sudo apt-get install python-dev

# Download virtualenv
wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py

# Install virtualenv 
mkdir $SHARE/virtualenv
ln -s $SHARE/virtualenv
python virtualenv.py virtualenv

# Activate virtualenv and install needed libraries
source virtualenv/bin/activate
pip install flask validictory regex

# clean up
rm virtualenv.pyc virtualenv.py
