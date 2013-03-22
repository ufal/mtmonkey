#!/bin/sh

PREFIX=/home/khresmoi/mt-stable/moses/usr
if [ -d /lib64 ]; then
LIBDIR=$PREFIX/lib64
else
LIBDIR=$PREFIX/lib
fi
export PATH=$PREFIX/bin${PATH:+:$PATH}
export LD_LIBRARY_PATH=$LIBDIR${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export LIBRARY_PATH=$LIBDIR${LIBRARY_PATH:+:$LIBRARY_PATH}
export CPATH=$PREFIX/include${CPATH:+:$CPATH}

