#!/bin/bash
# Quick setup script for initializing either a true can device or virtual one

if [ "$(id -u)" != "0" ]; then
	echo "Please run as root" 1>&2
	exit 1
fi

if [ "$1" == "-v" ]; then
    ip link set down vcan0
    exit 0;
fi

ip link set down can0