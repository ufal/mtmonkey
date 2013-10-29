#!/bin/bash

langs=(cs en_cs fr en_fr de en_de)

#c=1
    #clients=$[10*$c]
    for clients in 1 10
    do
    dir=logs_4l_$clients
    mkdir $dir #!!!
    for p in {0..9..3}
    do
        begin=$[10*$p]

        # languages
        for l1 in {0..2}
        do        
        for l2 in $(eval echo {$[$l1+1]..3})
        do
        for l3 in $(eval echo {$[$l2+1]..4})
        do
        for l4 in $(eval echo {$[$l3+1]..5})
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
                
                ./qqsub1g $dir runBULK/testBULK_${langs[$l1]}_${client}.shc 
                ./qqsub1g $dir runBULK/testBULK_${langs[$l2]}_${client}.shc 
                ./qqsub1g $dir runBULK/testBULK_${langs[$l3]}_${client}.shc 
                ./qqsub1g $dir runBULK/testBULK_${langs[$l4]}_${client}.shc 

            done
            echo submitted langs ${langs[$l1]} ${langs[$l2]} ${langs[$l3]} ${langs[$l4]} with start $begin and $clients clients
            while qstat -j 'testBULK*' &> /dev/null;do sleep 1; done
 
        # end languages
        done
        done
        done
        done

    done
done
