#!/bin/bash

for jtable in `ls -1 jtable_0.9*` ; do
    # echo "Playing $jtable"
    # cat ../testings/dataset.yml | ./${jtable} -p host_list
    cmd="cat ../testings/big_facts.json | ./${jtable} -p plays[0].tasks[0].hosts"
    echo "Running: $cmd>/dev/null"
    time eval $cmd>/dev/null
done    