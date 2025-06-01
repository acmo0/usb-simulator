# USB Simulator

<p align="center">
    <img src="docs/source/logo.svg">
<p>

## Introduction


`usbsimulator` is a Python 3 package which aims to simulate the signal sent on an USB bus based on the packets transmitted.
This package allows you to create multiple USB packets and simulate their transmission on the bus at a physical level.
The implementation has been on Debian 12.

Please the the documentation and examples here : http://doc.acmo0.org/introduction.html

## Motivation

This package has been developped in order to create two challenges for the French CTF [404CTF](https://www.404ctf.fr>) using only software, so that no particular hardware USB packet sniffer is needed. This module is entirely developped based on the USB1.1 specification for *full-speed* devices.
This specification can be found [here](http://esd.cs.ucr.edu/webres/usb11.pdf).

## Limitations

This module supports for now only USB full-speed transmissions, but for all kind of USB packets as defined in the USB1.1 specification. Moreover, some device requests are not supported.
