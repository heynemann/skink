'''Base class to support plugins'''

PLUGINS = []

class MetaSkinkPluginBase(type):
    def __init__(mls, name, bases, attrs):
        if name not in ('SkinkPlugin', ):
            # registering
            PLUGINS.append(mls)

        super(MetaSkinkPluginBase, mls).__init__(name, bases, attrs)

class SkinkPlugin(object):
    __metaclass__ = MetaSkinkPluginBase
    
    def __init__(self, server):
        self.server = server
        
        def on_build_successful(data):
            self.build_successful(data['server'], data['project'], data['build'])

        server.subscribe('on_build_successful', on_build_successful)

    def build_succesful(self, server, project, build):
        pass

    @classmethod
    def all(cls):
        return PLUGINS