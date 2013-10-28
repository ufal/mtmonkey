#!/bin/bash

function qqsub1gd() {
    dir=$1
    shift
    for i in $@
    do
        qsub -cwd -o $dir -e $dir -S /bin/bash -V -j n -l h_vmem=1g -l mem_free=1g $i
    done
}

#langs=(cs en_cs fr en_fr de en_de)

#c=1
    #clients=$[10*$c]
    for clients in 1 10 100 2 5 20 50
    do
    dir=logs_6l_$clients
    mkdir -p $dir #!!!
    rm $dir/*
    for p in {0..9..3}
    do
        begin=$[10*$p]
        # begin=0

        # languages
            starttime=$[$clients/3+5]
            starttime.pl $starttime #!!!
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
                
                qqsub1gd $dir runBULK/testBULK_*_${client}.shc #!!!

            done
            sleeptime=$[6*$clients+$starttime]
            echo submitted all langs with start $begin and $clients clients
            echo sleeping for $sleeptime
            sleep $sleeptime #!!!
        
    done
done
