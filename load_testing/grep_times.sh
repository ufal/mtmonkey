grep -h 'ms avg per line' logs_$1/testBulk_*.shc.o* | cut -f1 > times_$1
