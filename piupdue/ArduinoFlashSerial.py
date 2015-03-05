"""
Dealing with serial commands.
ReadWord(SerialPort, WriteAddress, Log) - Writes the address command and return the value in a 32 bit number.
ReadSerialByte(ser, Log) - Reads one byte of data from serial port.
ReadSerial(ser, Log) - return any data in serial port.
WriteWord(SerialPort, Addr, Value, Log) - Converts addr and value into message of format: W{addr},{value}# WXXXXXXXX,XXXXXXXX# and writes to serial port.
Write(SerialPort, Log, Addr, Data, DataSize) - Converts addr and value into message of format: S{addr},{value}# SXXXXXXXX,XXXXXXXX# and writes to serial port. Then uses WriteXmodem to transfer data.
Go(SerialPort, Log, Addr) - Converts addr into message of format: G{addr}# GXXXXXXXX# and writes to serial port.
"""
import time, binascii, sys
import ArduinoFlashHardValues, ArduinoFlashXmodem
       
def ReadWord(SerialPort, WriteAddress, Log):
    """ Writes to address and flips the received bits and stores in a 32 bit variable. """
    Log.Log("ReadWord(), Writing: " + WriteAddress)
    
    SerialPort.write(WriteAddress)
    
    data = ReadSerial(SerialPort, Log)
    
    value = (ord(data[3]) << 24 | ord(data[2]) << 16 | ord(data[1]) << 8 | ord(data[0]) << 0)  # ord() gives value of byte. Incase where data = {1,2,3,4}, value = 00000100 00000011 00000010 00000001, ie 4,3,2,1
     
    Log.Log("Value: " + str(value) + ", " + hex(value))
    
    return value

def ReadSerialByte(ser, Log):
    """ Reads one byte of data from serial port. """

    toBeRead = ser.inWaiting()
    
    if toBeRead > 0: 
        data = ser.read(1)
        
        Log.Log("Read data: " + data + ", " + binascii.hexlify(data))
        
        return data
    else:
        #Log.Log("No Data To Be Read") 
        return ""   

def ReadSerial(ser, Log):
    """ Reads any data in serial port. """
    time.sleep(2)
    while 1:

        toBeRead = ser.inWaiting()
        Log.Log("ReadSerial(), " + str(toBeRead) + " bytes in buffer.")
        
        if toBeRead > 0: 
            data = ser.read(toBeRead)
            
            hexData = ":".join("{:02x}".format(ord(c)) for c in data)       # Just for display purposes.
            
            Log.Log("Read data: " + data + "\nIn hex: " + hexData)
            
            return data
        else:
            Log.Log("No Data To Be Read")
            break    


def WriteWord(SerialPort, Addr, Value, Log):
    """ Converts addr and value into message of format: W{addr},{value}# WXXXXXXXX,XXXXXXXX# and writes to serial port."""
    addr = '{0:08X}'.format(Addr)
    value = '{0:08X}'.format(Value) 
        
    output = "W" + addr + "," + value + '#'                                 # W20001020,20010000#
    Log.Log("Writing Word: " + output)
    
    if ArduinoFlashHardValues.LiveWrite:
        SerialPort.write(output)
        
def Write(SerialPort, Log, Addr, Data, DataSize, IsNativePort):
    """ 
    Converts addr and value into message of format: S{addr},{value}# SXXXXXXXX,XXXXXXXX# and writes to serial port.
    Then uses WriteXmodem to transfer data.
    """
    addr = '{0:08X}'.format(Addr)
    size = '{0:08X}'.format(DataSize)

    output = "S" + addr + "," + size + '#'
    Log.Log("Writing: " + output)
    
    if ArduinoFlashHardValues.LiveWrite:
        SerialPort.write(output)
            
    if IsNativePort:
        ArduinoFlashXmodem.WriteBinary(SerialPort, Log, Data, len(Data))
    else:
        ArduinoFlashXmodem.WriteXmodem(SerialPort, Log, Data, DataSize)
        
def Go(SerialPort, Log, Addr):
    """ Converts addr into message of format: G{addr}# GXXXXXXXX# and writes to serial port."""
    addr = '{0:08X}'.format(Addr)
    
    output = "G" + addr + "#"                                               #snprintf((char*) cmd, sizeof(cmd), "G%08X#", addr); G20001020#

    Log.Log("Serial.Go(): " + output)
    
    if ArduinoFlashHardValues.LiveWrite:
        SerialPort.write(output)