'''Plugin to test the plug-in infrastructure'''

from skink.src.plugins.base import SkinkPlugin
from skink.src.models import *

class HelloWorldPlugin(SkinkPlugin):

   def build_successful(self, server, project, build):
       tab = BuildTab(name="Hello World", log="Hello Build!!!", build=build)
       build.tabs.append(tab)