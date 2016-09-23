#!/bin/bash

# run Moses server and MTMonkey inside Docker
#
# expects the following environment variables:
# CPU_CORES ... maximum number of threads (both MTMonkey and Moses Server)
# MTMONKEY_APPSERVER_URL ... URL of appserver to register to
# MTMONKEY_PASSPHRASE ... secret passphrase to authenticate worker with appserver
# MTMONKEY_PUBLIC_PORT ... actual port that we are visible on
# MTMONKEY_SRCLANG ... source language
# MTMONKEY_TGTLANG ... target langauge

MODELDIR="/mt-model"
MOSES_SERVER_PORT=9000
MTMONKEY_PORT=8080 # internal port, within the Docker container

function die() {
  echo "$@" >&2
  exit 1
}

[ -f "$MODELDIR/moses.ini" ] \
  || die "MT model files not provided. Mount a docker volume to /mt-model"

if [ -z "$MTMONKEY_APPSERVER_URL" ] \
  || [ -z "$MTMONKEY_PASSPHRASE" ] \
  || [ -z "$MTMONKEY_PUBLIC_PORT" ] \
  || [ -z "$MTMONKEY_SRCLANG" ] \
  || [ -z "$MTMONKEY_TGTLANG" ] ; then
  die "One of the required environment variables was not provided"
fi

# start Moses2 server
cd "$MODELDIR"
nohup /mosesdecoder/bin/moses2 \
  --threads $CPU_CORES --server --server-port $MOSES_SERVER_PORT -f moses.ini \
  |& sed 's/^/[MOSESSERVER] /' &
cd ..

# create config file for MTMonkey
cat << EOF > /worker.cfg
PORT = $MTMONKEY_PORT
PUBLIC_PORT = $MTMONKEY_PUBLIC_PORT
TRANSLATE_PORT = $MOSES_SERVER_PORT
SOURCE_LANG = $MTMONKEY_SOURCE_LANG
TARGET_LANG = $MTMONKEY_TARGET_LANG
THREADS = $CPU_CORES
APPSERVER_URL = $MTMONKEY_APPSERVER_URL
PASSPHRASE = $MTMONKEY_PASSPHRASE
EOF

exec python /mtmonkey/worker/src/worker.py -c /worker.cfg
