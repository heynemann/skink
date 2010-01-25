class Form(object):
    pass
    
class Input(object):
    
    def __init__(self, *args, **kwargs):
        self.attrs = kwargs
    
    def render(self):
        return u'<input type="%s" />' % self.type
        
    def __str__(self):
        return self.render()
        
class TextInput(Input):
    type = u'text'
        
class PasswordInput(Input):
    type = u'password'
    
class TextField(object):
    
    def __init__(self, widget=None):
        pass