#!/bin/bash
export ANSIBLE_STDOUT_CALLBACK=json
export ANSIBLE_SHOW_CUSTOM_STATS=true



for ini_file in $(find . -name hosts_dc*.ini) ; do
    inv_env=$(echo $ini_file | cut -d "/" -f2)
    dept=$(echo $ini_file | cut -d "/" -f3)
    file=$(echo $ini_file | cut -d "/" -f4-)
    cmd="ansible-playbook -i $ini_file play_view_inventoy_use_debug.yml"
    target_file=export_inv_${inv_env}_${dept}_$file.json
    echo "$cmd > $file" 
    eval "$cmd" > $target_file
    # json = "{\"file\": $ini_file }"

done