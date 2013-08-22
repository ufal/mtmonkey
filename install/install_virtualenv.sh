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

# Download and install virtualenv (change version for the latest here!)
wget https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.1.tar.gz
tar xvfz virtualenv-1.9.1.tar.gz

mkdir $SHARE/virtualenv
ln -s $SHARE/virtualenv .

cd virtualenv-1.9.1
python virtualenv.py /home/$USER/virtualenv
cd ..

# Activate virtualenv and install needed libraries
source virtualenv/bin/activate
pip install flask validictory regex configobj

# clean up
rm -rf virtualenv-1.9.1 virtualenv-1.9.1.tar.gz
