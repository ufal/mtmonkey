#!/bin/bash


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
                
                ./qqsub1g $dir runBULK/testBULK_*_${client}.shc

            done
            echo submitted all langs with start $begin and $clients clients
            while qstat -j 'testBULK*' &> /dev/null; ; do sleep 1; done
    done
done
