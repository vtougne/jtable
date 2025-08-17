#!/bin/bash

ref_doc=$1
new_doc=$2
exclude_patterns=$3


if [ -z "$ref_doc" ] || [ -z "$new_doc" ]; then
    echo "Usage: $0 <ref_doc> <new_doc> [exclude_patterns]"
    exit 1
fi

# echo debug exclude_patterns: $exclude_patterns
if [ ! -z "$exclude_patterns" ]; then
    exclude_cmd=" | egrep -v \"$exclude_patterns\"" 
    cmd="diff --side-by-side --suppress-common-lines $ref_doc $new_doc $exclude_cmd"
else
    cmd="diff --side-by-side --suppress-common-lines $ref_doc $new_doc"
fi

echo cmd: $cmd

return=$(eval "$cmd")
if [ -z "$return" ]; then
    echo "Success No differences found"
else
    echo "               =================== Differences ==================="
    echo "$return"
    echo "               ===================================================="
    echo "Error Differences found"
    exit 1
fi