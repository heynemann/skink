'''Plugin that runs PyLint against your codebase'''

from skink.src.plugins.base import SkinkPlugin
from skink.src.models import *

class PyLintPlugin(SkinkPlugin):

   def build_successful(self, server, project, build):
       project_config = server.context.settings.PyLintPlugin.modules
       project_config = [item.strip() for item in project_config.split(',')]
       project_config = dict([item.split(':') for item in project_config])

       if project.name not in project_config:
           return

       exit_code, log = self.shell("pylint %s" % project_config[project.name], self.get_project_path(server, project))
       tab = BuildTab(name="PyLint", log=log, build=build)
       build.tabs.append(tab)