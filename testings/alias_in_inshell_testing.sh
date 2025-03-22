#!/bin/bash

# alias bob='echo "bob"'
bob() { echo coucou; }
# bob
from_xml() { jtable -o "{{ stdin | from_xml() }}" ; }