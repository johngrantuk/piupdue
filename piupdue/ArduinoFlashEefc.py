""" Handles main processor operations.
WriteFileToFlash()
    LoadBuffer()
    WritePage()
EraseFlash()
SetBootFlash()
Reset()

Not sure what all are doing but tests have worked.
 """
import ArduinoFlashSerial, ArduinoFlashHardValues
import ctypes, time, os

def WriteFileToFlash(SerialPort, Log, File, IsNativePort):
    """
    Writes File to processors flash in blocks pageSize long.
    """
    Log.Log("Writing file to flash: " + File)

    pageSize = ArduinoFlashHardValues.size                                                      # Size of data blocks to be written.                                                                                                                   
    pageNum = 0
    offset = 0                                                                                  # -- Flash.h LN99 => 0
    numPages = 0
    onBufferA = True                                                                           # LN52 Flash.cpp

    fileSizeBytes = os.path.getsize(File)                                                       # Find file size.
    
    numPages = (fileSizeBytes + pageSize - 1) / pageSize                                        # 47 pages for blink.
    if numPages > ArduinoFlashHardValues.pages:
        raise Exception("WriteFlash()-File Size Error. numPages: " + str(numPages))

    Log.Log("Writing " + str(fileSizeBytes) + "bytes to flash in " + str(numPages) + " pages.")
    
    f = open(File, 'rb') 
    
    while True:
        piece = f.read(pageSize)                                                                # Reads a block of data from file.
        
        if not piece:
            Log.Log("End of file??")
            break
        
        readBytes = len(piece) 
        
        Log.Log("Read: " + str(readBytes) + "bytes from file. onBufferA: " + str(onBufferA) + ", PageNum: " + str(pageNum))
        
        dataJ = []

        for i in range(0, readBytes):
            dataJ.append(ord(piece[i]))
        
        LoadBuffer(SerialPort, Log, onBufferA, dataJ, IsNativePort)
        
        page = offset + pageNum
        onBufferA = WritePage(page, onBufferA, SerialPort, Log)

        pageNum += 1
        
        if pageNum == numPages or readBytes != pageSize:
            Log.Log("End of file...")
            break
    
    f.close()
    Log.Log("End of WriteFlash()\n")

def EraseFlash(SerialPort, Log):
    """ Erases processor flash. """
    Log.Log("EraseFlash():")
    
    WaitFSR(SerialPort, Log)
        
    WriteFCR0(ArduinoFlashHardValues.EEFC_FCMD_EA, 0, SerialPort, Log)
    
    WaitFSR(SerialPort, Log)
    
    WriteFCR1(ArduinoFlashHardValues.EEFC_FCMD_EA, 0, SerialPort, Log)
    
    Log.Log("Flash Erased.")
    
def LoadBuffer(SerialPort, Log, OnBufferA, Data, IsNativePort):
    """
    Writes SXXXXXXXX,XXXXXXXX# command then Xmodem.
    """
    Log.Log("LoadBuffer():")
    ArduinoFlashSerial.Write(SerialPort, Log, ArduinoFlashHardValues.pageBufferA if OnBufferA else ArduinoFlashHardValues.pageBufferB, Data, ArduinoFlashHardValues.size, IsNativePort)
    Log.Log("End of LoadBuffer()\n")
    

def WritePage(Page, OnBufferA, SerialPort, Log):
    """ LN256 EefcFlash """
    Log.Log("Write Page(), Page: " + str(Page) + ", OnBufferA: " + str(OnBufferA))
    
    SetDstAddr(ArduinoFlashHardValues.addr + Page * ArduinoFlashHardValues.size, SerialPort, Log)
    
    SetSrcAddr(ArduinoFlashHardValues.pageBufferA if OnBufferA else ArduinoFlashHardValues.pageBufferB, SerialPort, Log)   
    
    OnBufferA = not OnBufferA  
    
    WaitFSR(SerialPort, Log) 
    
    ArduinoFlashSerial.WriteWord(SerialPort, ArduinoFlashHardValues.reset, ArduinoFlashHardValues.start + 1, Log)                   # _wordCopy.runv();
    
    ArduinoFlashSerial.Go(SerialPort, Log, ArduinoFlashHardValues.stack + ArduinoFlashHardValues.user)                                                            # _wordCopy.runv();
     
    if ArduinoFlashHardValues.planes == 2 and Page >= ArduinoFlashHardValues.pages / 2:                                                                
        WriteFCR1(ArduinoFlashHardValues.EEFC_FCMD_EWP if ArduinoFlashHardValues.eraseAuto else ArduinoFlashHardValues.EEFC_FCMD_WP, Page - ArduinoFlashHardValues.pages / 2, SerialPort, Log)
    else:
        WriteFCR0(ArduinoFlashHardValues.EEFC_FCMD_EWP if ArduinoFlashHardValues.eraseAuto else ArduinoFlashHardValues.EEFC_FCMD_WP, Page, SerialPort, Log)

    Log.Log("End of Write Page()\n")
    return OnBufferA

def SetBootFlash(SerialPort, Log, Enable):
    """ Sets boot flash. """
    Log.Log("SetBootFlash():")
    WaitFSR(SerialPort, Log)
    WriteFCR0(ArduinoFlashHardValues.EEFC_FCMD_SGPB if Enable else ArduinoFlashHardValues.EEFC_FCMD_CGPB, 1, SerialPort, Log)
    WaitFSR(SerialPort, Log)
    time.sleep(1)
    Log.Log("End of SetBootFlash.")
    
def Reset(SerialPort, Log):
    """ Resets processor. """
    Log.Log("Reset()...")
    ArduinoFlashSerial.WriteWord(SerialPort, 0x400E1A00, 0xA500000D, Log)
    Log.Log("Reset done...")
    time.sleep(1)

def WaitFSR(SerialPort, Log):
    """ Not sure what it does. """
    Log.Log("WaitFSR():")
    tries = 0
    fsr1 = ctypes.c_uint32(0x1).value

    while tries <= 500:
    
        addr = "w" + '{0:08X}'.format(ArduinoFlashHardValues.EEFC0_FSR) + ",4#"
        Log.Log("Sending EEFC0_FSR: " + addr)
        
        if ArduinoFlashHardValues.LiveWrite:
            fsr0 = ArduinoFlashSerial.ReadWord(SerialPort, addr, Log)
            
            if fsr0 & (1 << 2):
                Log.Log("WaitFSR() Error. fsr0")
                
        addr = "w" + '{0:08X}'.format(ArduinoFlashHardValues.EEFC1_FSR) + ",4#"
        Log.Log("Sending EFC1_FSR: " + addr)

        if ArduinoFlashHardValues.LiveWrite:
            fsr1 = ArduinoFlashSerial.ReadWord(SerialPort, addr, Log)
        
            if fsr1 & (1 << 2):
                Log.Log("WaitFSR() Error. fsr1")
    
            if fsr0 & fsr1 & 0x1:
                Log.Log("Breaking.")
                break
            
            time.sleep(1)
        else:
            break
        
        tries += 1
    
    if tries > 500:
        Log.Log("WaitFSR() Error. Tried and failed!!")
    
def WriteFCR0(cmd, arg, SerialPort, Log):
    """ 
    writeFCR0(uint8_t cmd, uint32_t arg)
    writeFCR0(EEFC_FCMD_EA, 0); 
    EefcFlash.cpp LN314 _samba.writeWord(EEFC0_FCR, (EEFC_KEY << 24) | (arg << 8) | cmd); 
    """ 
    Log.Log("WriteFCR0()")
    value = (ArduinoFlashHardValues.EEFC_KEY << 24) | (arg << 8) | cmd
    
    ArduinoFlashSerial.WriteWord(SerialPort, ArduinoFlashHardValues.EEFC0_FCR, value, Log)

def WriteFCR1(cmd, arg, SerialPort, Log):
    """
    EefcFlash::writeFCR1(uint8_t cmd, uint32_t arg)
    _samba.writeWord(EEFC1_FCR, (EEFC_KEY << 24) | (arg << 8) | cmd); 
    """
    Log.Log("WriteFCR1()")
    value = (ArduinoFlashHardValues.EEFC_KEY << 24) | (arg << 8) | cmd
    
    ArduinoFlashSerial.WriteWord(SerialPort, ArduinoFlashHardValues.EEFC1_FCR, value, Log)
    
def SetDstAddr(DstAddr, SerialPort, Log):
    """ Unsure """
    Log.Log("SetDstAddr()")
    ArduinoFlashSerial.WriteWord(SerialPort, ArduinoFlashHardValues.user + ArduinoFlashHardValues.dstAddr, DstAddr, Log)    # WordCopyApplet (0x20001000 + 0x00000028), DstAddr
    
def SetSrcAddr(SrcAddr, SerialPort, Log):
    """ Unsure """
    Log.Log("SetSrcAddr()")
    ArduinoFlashSerial.WriteWord(SerialPort, ArduinoFlashHardValues.user + ArduinoFlashHardValues.srcAddr, SrcAddr, Log)    # WordCopyApplet (0x20001000 + 0x00000028), DstAddr