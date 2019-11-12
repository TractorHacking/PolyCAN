#!/bin/bash
# Quick setup script for initializing either a true can device or virtual one

if [ "$(id -u)" != "0" ]; then
	echo "Please run as root" 1>&2
	exit 1
fi

if [ -f /etc/os-release ] || [ -f /etc/lsb-release] || [ -f /etc/debian_version ]; then
    apt install can-utils -y
elif [ -f /etc/SuSe-release ] || [ -f /etc/redhat-release ]; then
    rpm -i can-utils -y
fi

if [ "$1" == "-v" ]; then
    modprobe vcan
    ip link add dev vcan0 type vcan
    ip link set up vcan0
    exit 0;
fi

# loopback for local testing the can
if [ "$1" == "-l" ]; then
    ip link set can0 up type can bitrate 250000 loopback on;
    exit 0;
fi

ip link set can0 up type can bitrate 250000;



