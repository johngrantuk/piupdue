""" Handles all incoming messages from the Master Controller Arduino serial port."""
import ArduinoFlashXmodem, Logger, ArduinoFlashSerial, ArduinoFlashEefc, ArduinoFlashHardValues
import time, serial, os
import traceback
import ctypes
import argparse

ser = 0
    
def SetSamBA():
    """ 
    Initial triggering of chip into SAM-BA mode. 
    On the Programming Port there is an ATMEGA16U2 chip, acting as a USB bridge to expose the SAM UART as USB. 
    If the host is connected to the programming port at baud rate 1200, the ATMEGA16U2 will assert the Erase pin and Reset pin of the SAM3X, forcing it to the SAM-BA bootloader mode. 
    The port remains the same number but to access SAM-BA Baud rate must be changed to 115200.
    """
    log.Log("Setting into SAM-BA...")
    
    ser = serial.Serial(port=ArduinoFlashHardValues.arduinoPort,\
                        baudrate=1200,\
                        parity=serial.PARITY_NONE,\
                        stopbits=serial.STOPBITS_ONE,\
                        bytesize=serial.EIGHTBITS,\
                        timeout=2000)
                        
    time.sleep(10)
    
    ser.close() 
    log.Log("SAM-BA Set.")                                                                    

def ConnectSamBA():
    """
    Connects to a processor that has been set into SAM-BA bootloader mode. (115200 Baud)
    Does some initialisation then checks Chip ID confirming correct processor.
    """  
    log.Log("ConnectSamBA()...")
    
    ser = serial.Serial(port=ArduinoFlashHardValues.arduinoPort,\
                        baudrate=115200,\
                        parity=serial.PARITY_NONE,\
                        stopbits=serial.STOPBITS_ONE,\
                        bytesize=serial.EIGHTBITS,\
                        xonxoff=False,\
                        timeout=None)
    
    log.Log("Openining at 115200...\n")  
                    
    time.sleep(5)
    
    ser.flushInput()

    log.Log("Writing 0x80...\n")
    ser.write('\x80')
    ArduinoFlashSerial.ReadSerial(ser, log)
    
    log.Log("Writing 0x80...\n")
    ser.write('\x80')
    ArduinoFlashSerial.ReadSerial(ser, log)

    log.Log("Writing #...\n")
    ser.write("\x23")
    ArduinoFlashSerial.ReadSerial(ser, log)

    log.Log("Setting into Binary mode (N#)...\n")
    ser.write("\x4E\x23")
    ArduinoFlashSerial.ReadSerial(ser, log)

    log.Log("Reading Chip ID...\n")
    
    chipId = ArduinoFlashSerial.ReadWord(ser, "\x77\x34\x30\x30\x45\x30\x39\x34\x30\x2C\x34\x23", log)
    
    log.Log("Chip ID: " + str(chipId) + ", " + hex(chipId))
    
    eproc = (chipId >> 5) & 0x7
    arch = (chipId >> 20) & 0xff
    
    log.Log("eproc: " + str(eproc) + ", " + hex(eproc))
    log.Log("arch: " + str(arch) + ", " + hex(arch))
       
    if eproc == 3:
        if arch >= 0x80 and arch <= 0x8a:                                                                               # Check for SAM3 architecture
            log.Log("Supported SAM3 processor.")
            return ser
        if arch >= 0x93 and arch <= 0x9a:
            log.Log("Supported SAM3 processor.")
            return ser
        
        log.Log("Unsupported Cortex-M3 architecture.")
        return False
    else:
        log.Log("Unsupported processor")
        return False
    
def ConnectSamBANative():
    """
    Connects to a processor that has been set into SAM-BA bootloader mode. (115200 Baud)
    Does some initialisation then checks Chip ID confirming correct processor.
    """  
    log.Log("ConnectSamBA()...")
    
    ser = serial.Serial(port=ArduinoFlashHardValues.arduinoPort,\
                        baudrate=921600,\
                        parity=serial.PARITY_NONE,\
                        stopbits=serial.STOPBITS_ONE,\
                        bytesize=serial.EIGHTBITS,\
                        xonxoff=False,\
                        timeout=None)
    
    log.Log("Openining at 921600...\n")  
                    
    time.sleep(5)
    
    ser.flushInput()

    log.Log("Setting into Binary mode (N#)...\n")
    ser.write("\x4E\x23")
    ArduinoFlashSerial.ReadSerial(ser, log)

    log.Log("Check for USER Address...\n")
    
    userAdd = ArduinoFlashSerial.ReadWord(ser, "w00000000,4#", log)
    log.Log("User addr: " + str(userAdd) + ", " + hex(userAdd))

    log.Log("Reading Chip ID...\n")
    
    chipId = ArduinoFlashSerial.ReadWord(ser, "\x77\x34\x30\x30\x45\x30\x39\x34\x30\x2C\x34\x23", log) # w400e0940,4#
    
    log.Log("Chip ID: " + str(chipId) + ", " + hex(chipId))
    
    eproc = (chipId >> 5) & 0x7
    arch = (chipId >> 20) & 0xff
    
    log.Log("eproc: " + str(eproc) + ", " + hex(eproc))
    log.Log("arch: " + str(arch) + ", " + hex(arch))
       
    if eproc == 3:
        if arch >= 0x80 and arch <= 0x8a:                                                                               # Check for SAM3 architecture
            log.Log("Supported SAM3 processor.")
            return ser
        if arch >= 0x93 and arch <= 0x9a:
            log.Log("Supported SAM3 processor.")
            return ser
        
        log.Log("Unsupported Cortex-M3 architecture.")
        return False
    else:
        log.Log("Unsupported processor")
        return False

def ArduinoFlashLoad(SketchFile, IsNativePort):
    """
    Loads a new sketch to Arduino Due.
    Sets into SAM-BA mode.
    Erases flash.
    Uploads new hex file.
    Sets boot flash.
    Resets processor.
    """
    
    log.Log("ArduinoFlashLoad()...")
    
    SetSamBA()                                                                                          # Sets processor into SAM-BA mode.
    
    serialPort = ConnectSamBANative()                                                                         # Connects to SAM-BA mode and confirms correct processor.
    if not serialPort:
        return
    
    length = ctypes.c_uint32(len(ArduinoFlashXmodem.code)).value
    ArduinoFlashSerial.Write(serialPort, log, ArduinoFlashHardValues.user, ArduinoFlashXmodem.code, length, IsNativePort)             # Writes the Xmodem hard code. Applet.cpp

    ArduinoFlashSerial.WriteWord(serialPort, ArduinoFlashHardValues.user + ArduinoFlashHardValues.words, ArduinoFlashHardValues.size / 4, log)     # 4 comes from sizeof(uint32_t) ie 4 bytes
        
    ArduinoFlashSerial.WriteWord(serialPort, ArduinoFlashHardValues.user + ArduinoFlashHardValues.stack, ArduinoFlashHardValues.user, log)                 # Set stack?
    
    ArduinoFlashSerial.WriteWord(serialPort, ArduinoFlashHardValues.EEFC0_FMR, (0x6 << 8), log)                                                     #  EefcFlash??
    
    ArduinoFlashSerial.WriteWord(serialPort, ArduinoFlashHardValues.EEFC1_FMR, (0x6 << 8), log)
        
    ArduinoFlashEefc.EraseFlash(serialPort, log)                                                                                                    # Erase Flash
    
    ArduinoFlashEefc.WriteFileToFlash(serialPort, log, SketchFile, IsNativePort)                                                                                        # Write new file
    
    ArduinoFlashEefc.SetBootFlash(serialPort, log, True)                                                                                            # Sets boot flash.
    
    ArduinoFlashEefc.Reset(serialPort, log)                                                                                                         # Resets processor.

    log.Log("Flash Loaded.")
	
def Checks(Port, SketchFile):
    """ Does basic checks that sketch file exists and port is connected."""
    if not os.path.isfile(SketchFile):
        raise Exception("Sketch File Does Not Exist: " + SketchFile)
    
    try:
        ser = serial.Serial(port=ArduinoFlashHardValues.arduinoPort,\
            baudrate=1200,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
            timeout=2000)
    except Exception:
        raise Exception("Error with Serial Port. " + traceback.format_exc())
    

def Test(Msg):
	print "This would be the file: " + Msg

if __name__ == "__main__":
    """ Main entry for program. """
    
    parser = argparse.ArgumentParser(description='Upload Arduino Sketch to Arduino Due via Pi.')
    
    parser.add_argument("-f", "--file", dest="sketchFile", required=True, help="Sketch file to upload. Including path.")
    parser.add_argument("-p", "--port", dest="port", required=True, help="Port Due is connected on.")
    parser.add_argument("-l", "--log", dest="logFile", default=False, help="Save output to log file.")
    
    args = parser.parse_args()
    
    sketchFile = args.sketchFile
    port = args.port
    logFile = args.logFile
    
    if not logFile:
        print "FILE: " + sketchFile + ", PORT: " + port + ", No Log File"
        log = Logger.Logger(False)                                                              # Doesn't save to Log, just prints.
    else:
        print "FILE: " + sketchFile + ", PORT: " + port + ", Log|: " + logFile
        log = Logger.Logger(True, logFile, True)                                                # Saves to Log file.
    
    log.Log("Starting ArduinoFlashLog.py")
        
    try:
        Checks(port, sketchFile)
        ArduinoFlashLoad(ArduinoFlashHardValues.sketchFile, ArduinoFlashHardValues.isNativePort)
        log.Log("Exiting ArduinoFlashLog.py")
    except Exception, e:
        log.Log("Main Exception:")
        log.Log(traceback.format_exc())