#!/bin/bash
#
# Installation of the Python environment for workers and appserver.
#
# Assuming $SHARE/virtualenv as the target directory and 
# ~$USER/virtualenv as the final destination of the virtualenv copies.
#

if [[ -z "$SHARE" || -z "$USER" ]]; then
    echo "Usage: USER=mtmonkey SHARE=/mnt/share install_virtualenv.sh"
    exit 1
fi

cd ~$USER  # comment this out if you do not want to install in home directory but current directory
DIR=`pwd`

# Check if we have python-dev installed
dpkg -s python-dev || sudo apt-get install python-dev

# Download and install virtualenv (change version for the latest here!)
VEVER=12.0.5
wget --no-check-certificate https://pypi.python.org/packages/source/v/virtualenv/virtualenv-$VEVER.tar.gz
tar xvfz virtualenv-$VEVER.tar.gz

mkdir $SHARE/virtualenv
ln -s $SHARE/virtualenv .

cd virtualenv-$VEVER
python virtualenv.py $DIR/virtualenv
cd ..

# Activate virtualenv and install needed libraries
source virtualenv/bin/activate
pip install flask validictory regex configobj requests

# clean up
rm -rf virtualenv-$VEVER virtualenv-$VEVER.tar.gz
