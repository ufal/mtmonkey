#!/bin/bash
#
# Linking directories for worker environment
#
# Assuming ~khresmoi/mt-$VERSION as the target directory
# and a shared directory $SHARE to be linked to, containing
# the following directories:
#
# git-$VERSION/ = Git checkout
# moses-$VERSION/ = Moses installation directory
# virtualenv/ = Python virtual environment

if [ -z $VERSION -o -z $SHARE ]; then
    print "Usage: VERSION=<stable|dev> SHARE=/export/NFS-SHARE/projects/khresmoi link_dirs.sh"
    exit 1
fi

cd ~khresmoi
# link to shared dir
ln -s $SHARE share

# create the main MT directory
mkdir mt-$VERSION
cd mt-$VERSION

# create worker-local directories
mkdir config logs models

# link to shared directories
ln -s $SHARE/moses-$VERSION moses
ln -s $SHARE/git-$VERSION/scripts
ln -s $SHARE/git-$VERSION/worker/src worker

# copy default config
cp $SHARE/git-$VERSION/config-example/* config
