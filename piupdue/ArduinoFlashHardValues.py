""" Hard coded values and settings."""
import ctypes

arduinoPort = '/dev/ttyACM1'
isNativePort = True
logFile = '/var/log/ScotSat/ArduinoFlash.log'
sketchFile = "/var/www/Testing/TestSketch1.cpp.bin"

LiveWrite = True

# Set by flashFactory when EefcFlash is first called. FlashFactory.cpp LN192, flash = new EefcFlash(samba, "ATSAM3X8", 0x80000, 2048, 256, 2, 32, 0x20001000, 0x20010000, 0x400e0a00, false);		
words = ctypes.c_uint32(0x00000030).value
stack = ctypes.c_uint32(0x00000020).value

eraseAuto = False                                    # set false on LN66 flasher.cpp when flash is erased.

planes = 2
pages = 2048
addr = ctypes.c_uint32(0x80000).value
user =  ctypes.c_uint32(0x20001000).value
regs = ctypes.c_uint32(0x400e0a00).value            # FlashFactory.cpp LN192
size = 256

dstAddr = 0x00000028                                # WordCopyArm.cpp
srcAddr = 0x0000002c

reset = user + 0x00000024                           # WordCopyApplet - addr + applet.reset
start = user + 0x00000000                           # WordCopyApplet - addr + applet.start

pageBufferA = user + 0x34 # _wordCopy.size()
pageBufferB = pageBufferA + size

EEFC0_FMR = regs + 0x00                             # EefcFlash.cpp
EEFC1_FMR = regs + 0x200
EEFC0_FSR = regs + 0x08
EEFC1_FSR = regs + 0x208
EEFC_KEY = 0x5a
EEFC_FCMD_EA = 0x5
EEFC0_FCR = regs + 0x04
EEFC1_FCR = regs + 0x204
EEFC_FCMD_EWP = 0x3
EEFC_FCMD_WP = 0x1

EEFC_FCMD_SGPB = 0xb
EEFC_FCMD_CGPB = 0xc