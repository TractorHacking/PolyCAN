## PolyCAN is a CAN bus analysis tool that allows you to record data coming from your John Deere Tractor.
___________

With the information gathered from PolyCAN you can use a variety of analysis tools in order to better understand the commands coming from the ECU. At this point PolyCAN is only availible for Linux.


For more information visit:
https://tractorhacking.github.io/polycan/

### PolyCAN Setup
______

Install:
`pip3 install git+https://github.com/TractorHacking/polycan`

Update:
`pip3 install git+https://github.com/TractorHacking/polycan --upgrade`

Usage:
`polycan`


#### To setup development enviorment:
1) Clone Repo
2) run `pip3 install -e path/to/repo/`


#### Known Issues:

There is currently an issue with accessing locally stored logs. If you log in upon running the application, there should be no issues.

<br>

### Hardware Setup
____

PolyCAN communicates only through a CAN interface and requires the `socketcan` driver and the `can-utils` package. The driver is included with Ubuntu and Debian based distros, but `can-utils` must be installed manually through your package manager of choice. 

Currently PolyCAN only recognizes native `can` and `vcan` devices. LinkLayer has created a very good [tutorial](https://wiki.linklayer.com/index.php/SocketCAN) on getting a native and virtual CAN device up and running.

In order to facilitate the setup and intialization of these devices, you can run `scripts/up.sh`. Using the flag `-l` will intialize your CAN interface in loopback mode if needed. Using the flag `-v` will intialize a virtual CAN device at `vcan0`.

Running `scripts/down.sh` will disable the interfaces. Use the `-v` flag when attempting to disable a virtual interface.

#### Raspberry Pi
Currently the Raspberry Pi has only been tested using the [RS485 CAN HAT](https://www.waveshare.com/rs485-can-hat.htm). However, the instructions here and the `scripts/pi_can_config.sh` setup script should function for any CAN device using the MCP2515 controller through the Raspberry Pi's SPI interface.

In order to utilize the SPI interface, you must first enable it through editing your Pi's configuration file. You must reboot your Pi after these changes have been made.

```
// add the following two lines to your /boot/config.txt file
dtparam=spi=on // this one exists, uncomment
dtoverlay=mcp2515-can0,oscillator=8000000,interrupt=25,spimaxfrequency=1000000
```

The quickest way to test this would be to run dmesg | grep -i '\(can\|spi\)’​ - should see something similar to the following output (at least this, there could be more).
```
[...] CAN device driver interface
[...] mcp251x spi0.0 can0: MCP2515 successfully initialized.
```
After you've confirmed setup, you can use the `scripts/up.sh` and `scripts/down.sh` as normal. 

You man also run `scripts/pi_can_config.sh` to have these steps performed for you.