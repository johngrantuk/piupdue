# piupdue
Python package that enables a compiled Ardunio Sketch to be uploaded to an Arduino Due from a RaspberryPI (connected by USB).

Based on the [Arduino BOSSA C++ source code.](https://github.com/shumatech/BOSSA/tree/arduino/src)

Install using: $ pip install pyupdue

Sketch file must be saved locally on PI and be of type ".cpp.bin".

# Run from cmd line

usage: piupdue.py [-h] -f SKETCHFILE [-p PORT] [-l LOGFILE]

optional arguments:

-h, --help            				show this help message and exit

-f SKETCHFILE, --file SKETCHFILE 	Sketch file to upload. Including path. (/path/File.cpp.bin)

-p PORT, --port PORT  				Port Due is connected on. Leave blank for auto selection.

-l LOGFILE, --log LOGFILE			Save output to log file.

# Use in Python Program

Use the Upload function found in piupdue.py, Ex:

import piupdue

piupdue.Upload('/usr/update/FastSketch.cpp.bin', '/dev/ttyACM1', '/var/log/piupdue.log')

# Some background

The Arduino Due is a microcontroller board based on the Atmel SAM3X8E ARM Cortex-M3 CPU. It is the first Arduino board based on a 32-bit ARM core microcontroller instead of the more common AVR. 
The different mcu means the performance is better but also means the booting process is different from the AVR, Ardunio has designed the board such that flashing firmware is easier than what the 
stock SAM3X has offered, [this link](http://playground.arduino.cc/Bootloader/DueBootloaderExplained) explains the booting process and the tricks that Arduiro implemented. 

The "avrdude" program is used to upload code to the AVR based Arduinos and there are quite a few examples of how to do this from the RaspberryPI. BOSSAC is used by Arduino to upload code to the ARM, 
it's the command line variation of [BOSSA](http://www.shumatech.com/web/products/bossa) which is a simple and open source flash programming utility for Atmel's SAM family of flash-based ARM microcontrollers 
designed to replace Atmel's SAM-BA software.

I required the ability to upload new code from a RaspberryPI to a Due. I couldn't find any info on getting BOSSAC to run on the PI so I have written this package in Python to replicate the fucntionality.


