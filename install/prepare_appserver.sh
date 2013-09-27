#!/bin/bash
#
# Copying all that is needed for appserver environment
#
# Assuming ~$USER as the target directory. 
#
# This will create the following directories:
#
# ~$USER/appserver-$VERSION = main directory for the appserver,
#   with the following subdirectories:
#
#   git/        = the Git repository of MTMonkey
#   scripts     = link to scripts directory in Git
#   appserver   = link to appserver/src directory in Git
#   config/     = directory for configuration files
#   logs/       = directory for log files
#
# Note that this will neither install Python virtualenv nor adjust
# the configuration in ~$USER/appserver-$VERSION/config/appserver.cfg .

if [[ -z "$VERSION" || -z "$USER" ]]; then
    echo "Usage: USER=username VERSION=version-name  prepare_appserver.sh"
    exit 1
fi

# create the main Appserver directory
cd /home/$USER
mkdir appserver-$VERSION
cd appserver-$VERSION

# Clone worker Git
git clone https://github.com/ufal/mtmonkey.git git

# Prepare subdirectories
mkdir -p config logs
ln -s git/appserver/src appserver
ln -s git/scripts scripts

# copy default config
cp git/config-example/appserver.cfg config

