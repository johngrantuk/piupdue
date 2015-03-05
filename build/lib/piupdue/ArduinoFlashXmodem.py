""" FlashXmodem Implementation."""
import ctypes, time
import ArduinoFlashHardValues, ArduinoFlashSerial

BLK_SIZE = 128
MAX_RETRIES = 20
code = [0x09, 0x48, 0x0a, 0x49, 0x0a, 0x4a, 0x02, 0xe0, 0x08, 0xc9, 0x08, 0xc0, 0x01, 0x3a, 0x00, 0x2a,0xfa, 0xd1, 0x04, 0x48, 0x00, 0x28, 0x01, 0xd1, 0x01, 0x48, 0x85, 0x46, 0x70, 0x47, 0xc0, 0x46,0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,0x00, 0x00, 0x00, 0x00]


def crc16Calc(Data, StartElement, Len):
    """ Calculates 2 Byte CRC """

    crc16Table = [0x0000,0x1021,0x2042,0x3063,0x4084,0x50a5,0x60c6,0x70e7,\
        0x8108,0x9129,0xa14a,0xb16b,0xc18c,0xd1ad,0xe1ce,0xf1ef,\
        0x1231,0x0210,0x3273,0x2252,0x52b5,0x4294,0x72f7,0x62d6,\
        0x9339,0x8318,0xb37b,0xa35a,0xd3bd,0xc39c,0xf3ff,0xe3de,\
        0x2462,0x3443,0x0420,0x1401,0x64e6,0x74c7,0x44a4,0x5485,\
        0xa56a,0xb54b,0x8528,0x9509,0xe5ee,0xf5cf,0xc5ac,0xd58d,\
        0x3653,0x2672,0x1611,0x0630,0x76d7,0x66f6,0x5695,0x46b4,\
        0xb75b,0xa77a,0x9719,0x8738,0xf7df,0xe7fe,0xd79d,0xc7bc,\
        0x48c4,0x58e5,0x6886,0x78a7,0x0840,0x1861,0x2802,0x3823,\
        0xc9cc,0xd9ed,0xe98e,0xf9af,0x8948,0x9969,0xa90a,0xb92b,\
        0x5af5,0x4ad4,0x7ab7,0x6a96,0x1a71,0x0a50,0x3a33,0x2a12,\
        0xdbfd,0xcbdc,0xfbbf,0xeb9e,0x9b79,0x8b58,0xbb3b,0xab1a,\
        0x6ca6,0x7c87,0x4ce4,0x5cc5,0x2c22,0x3c03,0x0c60,0x1c41,\
        0xedae,0xfd8f,0xcdec,0xddcd,0xad2a,0xbd0b,0x8d68,0x9d49,\
        0x7e97,0x6eb6,0x5ed5,0x4ef4,0x3e13,0x2e32,0x1e51,0x0e70,\
        0xff9f,0xefbe,0xdfdd,0xcffc,0xbf1b,0xaf3a,0x9f59,0x8f78,\
        0x9188,0x81a9,0xb1ca,0xa1eb,0xd10c,0xc12d,0xf14e,0xe16f,\
        0x1080,0x00a1,0x30c2,0x20e3,0x5004,0x4025,0x7046,0x6067,\
        0x83b9,0x9398,0xa3fb,0xb3da,0xc33d,0xd31c,0xe37f,0xf35e,\
        0x02b1,0x1290,0x22f3,0x32d2,0x4235,0x5214,0x6277,0x7256,\
        0xb5ea,0xa5cb,0x95a8,0x8589,0xf56e,0xe54f,0xd52c,0xc50d,\
        0x34e2,0x24c3,0x14a0,0x0481,0x7466,0x6447,0x5424,0x4405,\
        0xa7db,0xb7fa,0x8799,0x97b8,0xe75f,0xf77e,0xc71d,0xd73c,\
        0x26d3,0x36f2,0x0691,0x16b0,0x6657,0x7676,0x4615,0x5634,\
        0xd94c,0xc96d,0xf90e,0xe92f,0x99c8,0x89e9,0xb98a,0xa9ab,\
        0x5844,0x4865,0x7806,0x6827,0x18c0,0x08e1,0x3882,0x28a3,\
        0xcb7d,0xdb5c,0xeb3f,0xfb1e,0x8bf9,0x9bd8,0xabbb,0xbb9a,\
        0x4a75,0x5a54,0x6a37,0x7a16,0x0af1,0x1ad0,0x2ab3,0x3a92,\
        0xfd2e,0xed0f,0xdd6c,0xcd4d,0xbdaa,0xad8b,0x9de8,0x8dc9,\
        0x7c26,0x6c07,0x5c64,0x4c45,0x3ca2,0x2c83,0x1ce0,0x0cc1,\
        0xef1f,0xff3e,0xcf5d,0xdf7c,0xaf9b,0xbfba,0x8fd9,0x9ff8,\
        0x6e17,0x7e36,0x4e55,0x5e74,0x2e93,0x3eb2,0x0ed1,0x1ef0]
    
    crc16 = ctypes.c_uint16(0).value
    
    for x in range(StartElement, Len + StartElement):
        crc16 = (crc16 << 8) ^ ctypes.c_uint16(crc16Table[((crc16 >> 8) ^ ctypes.c_uint8(Data[x]).value) & 0xff]).value
        
        crc16 = ctypes.c_uint16(crc16).value

    return crc16

def Crc16Add(Data):
    """ Calculates two byte CRC and adds to end of Data array."""

    crc16 = ctypes.c_uint16(crc16Calc(Data, 3, BLK_SIZE)).value
    
    Data[BLK_SIZE + 3] = (crc16 >> 8) & 0xff
    Data[BLK_SIZE + 4] = crc16 & 0xff
    
def WriteBinary(SerialPort, Log, Data, Size):
    """ Writes all data to serial port. _port->write(buffer, size) != size"""
    Log.Log("WriteBinary()...")
    Log.Log("Writing bytes: " + str(Size))
    
    blkStr = ""
    for e in Data:
        blkStr = blkStr + chr(e)
    
    if ArduinoFlashHardValues.LiveWrite:
        bytesWritten = SerialPort.write(blkStr)
        Log.Log("Bytes written: " + str(bytesWritten))
        
        if bytesWritten != Size:
            raise Exception("WriteBinary() Exception.")
        

def WriteXmodem(SerialPort, log, Data, Size):
    """ Main implementation of Xmodem(). See Samba.cpp LN392 """
    log.Log("\n\nWriteXmodem():")  
    
    blkNum = 1                                                          # Block numbers haven't been implemented yet.
    blk = [ctypes.c_uint8(0).value] * (BLK_SIZE + 5)                    # Initial decleration of blk array.
 
    for retries in range(0, MAX_RETRIES):
        log.Log("Waiting for start char, C.")
        
        if ArduinoFlashHardValues.LiveWrite:
            receivedMsg = ArduinoFlashSerial.ReadSerialByte(SerialPort, log)
        else:
            receivedMsg = 'C'
        
        if receivedMsg == 'C':
            break
        
    if retries == MAX_RETRIES - 1:
        raise Exception("WriteXmodem() Waited Max For Start Char.")
    
    codeNo = 0
    bytesWritten = 0
    while Size > 0:
        
        blk[0] = ctypes.c_uint8(0x01).value                                # First three bytes are pre-filled.
        blk[1] = ctypes.c_uint8(blkNum & 0xff).value
        blk[2] = ctypes.c_uint8(~(blkNum & 0xff)).value
        
        log.Log("len(Data): " + str(len(Data)) + ", min: " + str(min(Size, BLK_SIZE)))
        log.Log("!. Code No: " + str(codeNo))
        
        if codeNo < len(Data):
            for x in range(3, min(len(Data), BLK_SIZE) + 3):                                       # Fills blk array (starting from 3rd element) with Data bytes.
                blk[x] = Data[codeNo]
                codeNo = codeNo + 1
            
        log.Log("2. Code No: " + str(codeNo))
        
        if Size < BLK_SIZE:                                                 # Fills any unwritten elements with 0 BLK_SIZE=128.
            log.Log("Filling in 0s.")
            for x in range(3 + len(Data), BLK_SIZE):
                blk[x] = 0x00
            
        Crc16Add(blk)                                                       # Calculates two byte CRC and adds to end of blk.
        
        i = 0                                                               # For display purpose.
    
        log.Log("Converting Xmodem CRC Code into string for serial transfer.")
        blkStr = ""
        for e in blk:
            blkStr = blkStr + chr(e)
            
        line = 0
        i = 0                                                               # For display purpose.
        dataStr = "Writing Data: \n0. "
        for e in blk:
            dataStr = dataStr + hex(e) + " "
            
            if (i + 1)%16 == 0:
                line += 1
                dataStr = dataStr + "\n" + str(line) + ". "
                
            i += 1
    
        log.Log(dataStr)
        
        for retries in range(0, MAX_RETRIES):
            log.Log("WriteXmodem(), writing Xmodem CRC Code data...")
            if ArduinoFlashHardValues.LiveWrite:
                bytesWritten = SerialPort.write(blkStr)   
                                                            # Write to the SAM-BA
            log.Log("WriteXmodem(), xModem CRC Code data written. " + str(bytesWritten))
            log.Log("WriteXmodem(), checking for ACK...")
            time.sleep(1)
            
            if ArduinoFlashHardValues.LiveWrite:
                receivedMsg = ArduinoFlashSerial.ReadSerialByte(SerialPort, log)
            else:
                receivedMsg = '\x06'
            
            if receivedMsg == '\x06':
                break
            
            time.sleep(3)
            
        if retries == MAX_RETRIES - 1:
            raise Exception("WriteXmodem() Waited While Writing Blk.")
        
        log.Log("Size: " + str(Size))
        Size = Size - BLK_SIZE
        blkNum = blkNum + 1
        log.Log("Size: " + str(Size))
    
    for retries in range(0, MAX_RETRIES):
        
        log.Log("ACK receive, writing EOT...")
        SerialPort.write('\x04')                                        # 0x04 = EOT
    
        log.Log("Waiting for ACK.") 
        time.sleep(1) 
        
        if ArduinoFlashHardValues.LiveWrite:
            receivedMsg = ArduinoFlashSerial.ReadSerialByte(SerialPort, log)
        else:
            receivedMsg = '\x06'
        
        if receivedMsg == '\x06':
            log.Log("ACK received.")
            log.Log("WriteXmodem() Complete.")
            break 
        
        time.sleep(3)
    
    if retries == MAX_RETRIES - 1:
        raise Exception("WriteXmodem() Waited While Writing EOT.") 
        
    log.Log("WriteXmodem() Complete.\n")