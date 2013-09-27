#!/bin/bash
#
# Copying all that is needed for worker environment
#
# Assuming ~$USER as the target directory
# and a shared directory $SHARE as the source, containing
# the following directories:
#
# moses-$VERSION/ = Moses installation directory
# virtualenv/ = Python virtual environment
#
# This will create the following directories:
#
# ~$USER/virtualenv = a copy of Python virtualenv 
#   - shared across MT versions
# ~$USER/mt-$VERSION = main directory for MT, 
#   with the following subdirectories:
#
#   git/    = the Git repository of MTMonkey
#   scripts = link to scripts directory in Git
#   worker  = link to worker/src directory in Git
#   moses/  = a copy of Moses
#   config/ = directory for configuration files
#   logs/   = directory for log files
#   models/ = directory for MT models
#

if [[ -z "$VERSION" || -z "$SHARE" || -z "$USER" ]]; then
    echo "Usage: USER=khresmoi VERSION=<stable|dev> SHARE=/mnt/share [LOGIN=\"user@host\"] [PORTS=\"7001:8081:9001\"]  prepare_worker.sh"
    exit 1
fi

if [[ -n "$LOGIN" ]]; then
    USERHOST=$LOGIN
    LOGIN="-e ssh $LOGIN:" # prepare parameter for rsync
fi

# copy virtualenv
cd /home/$USER
rsync -avs $LOGIN$SHARE/virtualenv .

# create the main MT directory
mkdir mt-$VERSION
cd mt-$VERSION

# copy Moses
rsync -avs $LOGIN$SHARE/moses-$VERSION/* moses/

# Clone worker Git
git clone https://github.com/ufal/mtmonkey.git git

# create worker-local directories
mkdir config logs models

# link to Git directories
ln -s git/scripts
ln -s git/worker/src worker

# copy default config
cp git/config-example/{config_moses.sh,config_remote.sh,worker.cfg} config

# override share settings according to the source share
sed -i -r "/^export REMOTE=/s:=.*$:=$SHARE:;" config/config_remote.sh
if [[ -n "$LOGIN" ]]; then
    sed -i -r "/export LOGIN=/s/^.*$/export LOGIN=$USERHOST/;" config/config_remote.sh
fi

# override ports settings
if [[ -n "$PORTS" ]]; then
    IFS=: read WORKER_PORT TRANSL_PORT RECASE_PORT <<< "$PORTS"
    sed -i -r "/export RECASER_PORT/s/= *[0-9]*/=$RECASE_PORT/;/export TRANSL_PORT/s/= *[0-9]*/=$TRANSL_PORT/" config/config_moses.sh
    sed -i -i "/^PORT/s/= *[0-9]*/= $WORKER_PORT/;/^TRANSLATE_PORT/s/= *[0-9]*/= $TRANSL_PORT/;/^RECASE_PORT/s/= *[0-9]*/= $RECASE_PORT/" config/worker.cfg
fi
