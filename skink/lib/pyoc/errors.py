class MessageBasedError(Exception):
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return self.message

class ContainerNotConfiguredError(MessageBasedError):
    def __init__(self):
        super(ConfigureError, self).__init__("The container has not yet been configured. Try calling IoC.configure first passing a valid configure source.")
        
    def __str__(self):
        return self.message
    
class CyclicalDependencyError(MessageBasedError):
    def __init__(self, message):
        super(CyclicalDependencyError, self).__init__(message)
        
    def __str__(self):
        return self.message
