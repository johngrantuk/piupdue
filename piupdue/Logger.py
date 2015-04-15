import time, logging, logging.handlers
from datetime import datetime
import os.path

class Logger:
    saveToLog = False
    display = True
    my_logger = False
    sockJs = False
    
    def __init__(self, SaveToLog, FilePath="\piupdue.log", Display=True, SockJs=False):
        
        if SaveToLog:
            self.saveToLog = SaveToLog
            self.filePath = FilePath
            self.display = Display
            self.sockJs = SockJs
            self.my_logger = logging.getLogger(FilePath)
            self.my_logger.setLevel(logging.DEBUG)
           
            handler = logging.handlers.RotatingFileHandler(FilePath, maxBytes='2000000', backupCount=5)       # Add the log message handler to the logger
            self.my_logger.addHandler(handler)
    
    def Log(self, Message):
        """ Saves message and timestamp to logfile."""
        Message = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3] + ", " + Message

        if self.sockJs:
            self.sockJs.broadcast(self.sockJs._connected, Message)
            
        if self.display:
            print Message     
            
        if self.saveToLog:
            if not os.path.isfile(self.filePath):
                raise Exception(self.filePath + " Log File Broken!!")
              
            self.my_logger.debug(Message)