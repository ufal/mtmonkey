#!/bin/bash

for p in {0..9}
do
    starttime.pl 20
    for l in cs fr de en_cs en_fr en_de
    do
        #qqsub1g runBULK/testBULK_${l}_??.shc
        qqsub1g runBULK/testBULK_${l}_?${p}.shc
        #qqsub1g runBULK/testBULK_${l}_6${p}.shc
        #echo submitted jobs for $l
    done
    echo submitted jobs for part $p
    #qstatw
    sleep 120
done


