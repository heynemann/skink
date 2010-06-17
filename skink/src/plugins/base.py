'''Base class to support plugins'''
from os.path import join, dirname, abspath

import skink.lib

from cleese import Executer, Status

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

    def fix_name(self, name):
        return name.strip().replace(" ", "")

    def get_project_path(self, server, project):
        project_name = self.fix_name(project.name)
        repository_path = join(server.build_dir, project_name)
        
        return repository_path

    def shell(self, command, base_path=None):
        executer = Executer(command=command, working_dir=base_path)

        executer.execute()

        while not executer.poll():
            pass
        
        return executer.result.exit_code, executer.result.log

    @classmethod
    def all(cls):
        return PLUGINS