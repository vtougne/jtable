#!/bin/bash

if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo or as root."
    exit 1
fi

[ -L /usr/local/bin/jtable ] &&  unlink /usr/local/bin/jtable

ln -s /project/jtable/archives/jtable_0.6.41_c.py /usr/local/bin/jtable

cd ../doc/examples/
../../make_doc.py -i doc_script.yml -o ../../archives/README.md $@