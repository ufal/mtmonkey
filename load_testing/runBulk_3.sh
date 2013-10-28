#!/bin/bash

function qqsub1g() {
    qsub -cwd -o $2 -e $2 -S /bin/bash -V -j n -l h_vmem=1g -l mem_free=1g $1
}

langs=(cs en_cs fr en_fr de en_de)

#c=1
    #clients=$[10*$c]
    for clients in 1 10
    do
    dir=logs_3l_$clients
    mkdir $dir #!!!
    for p in {0..9..3}
    do
        begin=$[10*$p]

        # languages
        for l1 in {0..3}
        do        
        for l2 in $(eval echo {$[$l1+1]..4})
        do
        for l3 in $(eval echo {$[$l2+1]..5})
        do
            
            starttime=$[$clients/4+5]
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
                
                qqsub1g runBULK/testBULK_${langs[$l1]}_${client}.shc $dir #!!!
                qqsub1g runBULK/testBULK_${langs[$l2]}_${client}.shc $dir #!!!
                qqsub1g runBULK/testBULK_${langs[$l3]}_${client}.shc $dir #!!!

            done
            sleeptime=$[3*$clients+$starttime+5]
            echo submitted langs ${langs[$l1]} ${langs[$l2]} ${langs[$l3]} with start $begin and $clients clients
            echo sleeping for $sleeptime
            sleep $sleeptime #!!!
        
        # end languages
        done
        done
        done

    done
done
