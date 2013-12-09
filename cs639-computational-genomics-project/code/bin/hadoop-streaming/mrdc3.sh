#!/bin/bash
#
# mrdc3.sh
#
# Created by Kartik Thapar on 12/06/2013 at 02:34:25
# Copyright (c) 2013 Kartik Thapar. All rights reserved.
#

rDepth=0
rLength=0
rDigits=0

inputFile=$1
echo "Running map reduce for input file: $inputFile"

# ----- Calculate number of digits -----
while read f
do
    rLength=${#f}
done < <(hadoop dfs -cat $inputFile)

rDigits=0
while [[ $rLength > 0 ]]; do
    rLength=$(($rLength/10))
    rDigits=$(($rDigits+1))
done

# ----- run as if depth=0

initialcmd="hadoop jar $HSTREAMING \
-file mapper-r-phase.py -mapper \"mapper-r-phase.py $rDigits $rDepth\" \
-file reducer-r-phase.py -reducer reducer-r-phase.py \
-input $inputFile \
-output /ktsa/output_0"
eval "$initialcmd"

echo "------------------------------------------------------------------------------------------"

duplicatesExist=$(hadoop dfs -cat /ktsa/output_0/part-00000 | awk -F '\t' '{print $1}')

while [[ "$duplicatesExist" == *True* ]]; do
    cmd="hadoop jar $HSTREAMING \
-file mapper-r-phase.py -mapper \"mapper-r-phase.py $rDigits $rDepth\" \
-file reducer-r-phase.py -reducer reducer-r-phase.py \
-input /ktsa/output_$rDepth/part-00000 \
-output /ktsa/output_$(($rDepth+1))"
    eval "$cmd"

    echo "------------------------------------------------------------------------------------------"

    # get value if duplicatesExist is true or false and recurse accordingly
    while read f
    do
        if [[ "$f" == *True* ]]; then
            duplicatesExist='True'
        else
            duplicatesExist='False'
        fi
    done < <(hadoop dfs -cat /ktsa/output_$(($rDepth+1))/part-00000 | awk -F '\t' '{print $1}')

    rDepth=$(($rDepth+1))
done

maxDepth=$rDepth

# # ----- UNFOLD RECURSION -----

suffixarraycmd="hadoop jar /usr/local/Cellar/hadoop/Current/libexec/contrib/streaming/hadoop-streaming-1.2.1.jar \
-file mapper-sortedall.py -mapper \"mapper-sortedall.py $maxDepth $rDepth $rDigits\" \
-file reducer-sortedall.py -reducer reducer-sortedall.py \
-input /ktsa/output_$rDepth/part-00000 \
-output /ktsa/currentsuffixarray"
eval "$suffixarraycmd"

rDepth=$(($rDepth-1))

echo "------------------------------------------------------------------------------------------"

while [[ $rDepth > -1 ]];
do
    while read currentsuffixarray
    do
        deletesuffixarraycmd="hadoop dfs -rmr /ktsa/currentsuffixarray*"
        $deletesuffixarraycmd

        cmd="hadoop jar /usr/local/Cellar/hadoop/Current/libexec/contrib/streaming/hadoop-streaming-1.2.1.jar \
-file mapper-sortedall.py -mapper \"mapper-sortedall.py $maxDepth $rDepth $rDigits '$currentsuffixarray'\" \
-file reducer-sortedall.py -reducer reducer-sortedall.py \
-input /ktsa/output_$rDepth/part-00000 \
-output /ktsa/currentsuffixarray"
        
        eval "$cmd"

    done < <(hadoop dfs -cat /ktsa/currentsuffixarray/part-00000 | awk -F '\t' '{print $1}')

    echo "------------------------------------------------------------------------------------------"

    rDepth=$(($rDepth-1))
done

