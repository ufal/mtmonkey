#!/bin/bash

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && dirname `pwd` )"

export MODELS_DIR=$BASEDIR/models/deen

# comment these two lines out if you do not need a recaser
export RECASER_PORT=9001
export RECASER_INI=$MODELS_DIR/recaser.moses.ini

export TRANSL_PORT=8081
export TRANSL_INI=$MODELS_DIR/moses.ini
