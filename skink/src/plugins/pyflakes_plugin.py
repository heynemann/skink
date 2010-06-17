'''Plugin that runs PyFlakes against your codebase'''

from skink.src.plugins.base import SkinkPlugin
from skink.src.models import *

class PyFlakesPlugin(SkinkPlugin):

   def build_successful(self, server, project, build):
       exit_code, log = self.shell("pyflakes .", self.get_project_path(server, project))
       tab = BuildTab(name="PyFlakes", log=log, build=build)
       build.tabs.append(tab)