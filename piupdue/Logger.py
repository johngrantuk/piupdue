import time, logging, logging.handlers
from datetime import datetime
import os.path

class Logger:
    saveToLog = False
    display = True
    my_logger = False
    
    def __init__(self, SaveToLog, FilePath="\piupdue.log", Display=True):
        
        if SaveToLog:
            self.saveToLog = SaveToLog
            self.filePath = FilePath
            self.display = Display
            self.my_logger = logging.getLogger('ArduinoFlashLogger')
            self.my_logger.setLevel(logging.DEBUG)
           
            handler = logging.handlers.RotatingFileHandler(FilePath, maxBytes='2000000', backupCount=5)       # Add the log message handler to the logger
            self.my_logger.addHandler(handler)
    
    def Log(self, Message):
        """ Saves message and timestamp to logfile."""
        Message = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3] + ", " + Message

        if self.display:
            print Message     
            
        if self.saveToLog:
            print "Saving..."
            if not os.path.isfile(self.filePath):
                raise Exception(self.filePath + " Log File Broken!!")
              
            self.my_logger.debug(Message)