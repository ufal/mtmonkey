grep -h 'ms avg per line' logs_$1/testBULK_*.shc.o* | cut -f1 > times_$1
