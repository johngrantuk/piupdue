import time, logging, logging.handlers
from datetime import datetime
import os.path

class Logger:
    display = True
    my_logger = False
    
    def __init__(self, FilePath, Display):
        self.filePath = FilePath
        Logger.display = Display
        Logger.my_logger = logging.getLogger('ArduinoFlashLogger')
        Logger.my_logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(FilePath, maxBytes='2000000', backupCount=5)       # Add the log message handler to the logger
        Logger.my_logger.addHandler(handler)
    
    def Log(self, Message):
        """ Saves message and timestamp to logfile."""
        Message = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S:%f')[:-3] + ", " + Message
        
        if Logger.display:
            print Message     
            
        if not os.path.isfile(self.filePath):
            raise Exception(self.filePath + " Log File Broken!!")
          
        Logger.my_logger.debug(Message)