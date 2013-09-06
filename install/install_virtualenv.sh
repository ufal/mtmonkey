#!/bin/bash
#
# Installation of the Python environment for workers and appserver.
#
# Assuming $SHARE/virtualenv as the target directory and 
# ~$USER/virtualenv as the final destination of the virtualenv copies.
#

if [ -z $SHARE -o -z $USER ]; then
    print "Usage: USER=khresmoi SHARE=/mnt/share install_virtualenv.sh"
    exit 1
fi

cd ~$USER

# Check if we have python-dev installed
dpkg -s python-dev || sudo apt-get install python-dev

# Download and install virtualenv (change version for the latest here!)
VEVER=1.9.1
wget https://pypi.python.org/packages/source/v/virtualenv/virtualenv-$VEVER.tar.gz
tar xvfz virtualenv-$VEVER.tar.gz

mkdir $SHARE/virtualenv
ln -s $SHARE/virtualenv .

cd virtualenv-$VEVER
python virtualenv.py /home/$USER/virtualenv
cd ..

# Activate virtualenv and install needed libraries
source virtualenv/bin/activate
pip install flask validictory regex configobj

# clean up
rm -rf virtualenv-$VEVER virtualenv-$VEVER.tar.gz virtualenv
