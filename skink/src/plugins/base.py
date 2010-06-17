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
            sets = data['server'].context.settings
            project = data['project']
            plugin_name = self.__class__.__name__
            
            if sets.config.has_section(plugin_name) \
                and sets.config.get(plugin_name, 'exclude'):

                exclude = sets.config.get(plugin_name, 'exclude')
                exclude = [item.strip() for item in exclude.split(',')]
                if project.name in exclude:
                    return

            self.build_successful(data['server'], data['project'], data['build'])

        server.subscribe('on_before_build_successful', on_build_successful)

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