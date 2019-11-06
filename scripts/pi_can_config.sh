#!/bin/bash

if [ "$(id -u)" != "0" ]; then
	echo "Please run as root" 1>&2
	exit 1
fi

echo "dtparam=spi=on" >> /boot/config.txt 
echo "dtoverlay=mcp2515-can0,oscillator=8000000,interrupt=25,spimaxfrequency=1000000" >> /boot/config.txt

echo "Configuration completed, please reboot your pi."