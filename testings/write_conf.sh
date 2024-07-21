#!/bin/bash



detect_root_user() {
    if [ "$EUID" -ne 0 ]; then
        echo "Please run as root"
        exit
    fi
}