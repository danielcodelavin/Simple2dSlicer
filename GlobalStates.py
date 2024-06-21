
class GlobalStates:
    _instance = None
    def __init__(self):
         self.scaler = 1
         self.frame = None
         self.firsttime = True
    @staticmethod
    def getInstance():
        """ Static access method. """
        if GlobalStates._instance is None:
            GlobalStates()
        return GlobalStates._instance

    def __init__(self):
        """ Virtually private constructor. """
        if GlobalStates._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            GlobalStates._instance = self
            self.scaler = 1  # Example of a global variable

    def get_scaler(self):
        """ Access the value of scaler. """
        return self.scaler

    def set_scaler(self, value):
        """ Set the value of scaler. """
        self.scaler = value
    def get_frame(self):
        """ Get the frame variable. """
        return self.frame
    
    def set_frame(self, value):
        """ Set the frame variable. """ 
        self.frame = value

    def get_firsttime(self):
        """ Get the firsttime variable. """
        return self.firsttime
    
    def set_firsttime(self, value):
        """ Set the firsttime variable. """
        self.firsttime = value
    
    
    
        