#!/bin/bash

for p in {0..9}
do
    for l in cs en_cs fr en_fr de en_de
    do
        starttime.pl 60
        #qqsub1g runBULK/testBULK_${l}_6${p}.shc
        #qqsub1g runBULK/testBULK_${l}_?${p}.shc
        qqsub1g runBULK/testBULK_${l}_??.shc
        #echo submitted jobs for $l
        sleep 300
    done
    echo submitted jobs for part $p
    #qstatw
done

