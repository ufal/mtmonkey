#!/bin/bash

function qqsub1g() {
    qsub -cwd -o $2 -e $2 -S /bin/bash -V -j n -l h_vmem=1g -l mem_free=1g $1
}

for c in {1..10}
do
    clients=$[10*$c]
    dir=logs_$clients
    mkdir $dir
    for p in {0..9}
    #for p in {0..9..4}
    do
        begin=$[10*$p]
        for l in cs en_cs fr en_fr de en_de
        do
            starttime=$[$c+5]
            starttime.pl $starttime
            for i in $(eval echo {1..${clients}})
            do
                client=$[$begin+$i-1]
                if [ $client -ge 100 ]
                then
                    client=$[$client-100]
                fi
                if [ $client -lt 10 ]
                then
                    client=0$client
                fi
                qqsub1g runBULK/testBULK_${l}_${client}.shc $dir
            done
            sleeptime=$[10*$c+$starttime]
            echo submitted lang $l with start $begin and $clients clients
            echo sleeping for $sleeptime
            sleep $sleeptime
        done
    done
done

