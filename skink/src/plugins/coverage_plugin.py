'''Plugin that gathers coverage data'''

from os.path import exists, join

from skink.src.plugins.base import SkinkPlugin
from skink.src.models import *

class CoveragePlugin(SkinkPlugin):

    def build_successful(self, server, project, build):
        self.register_coverage(server, project, build)

    def build_failed(self, server, project, build):
        self.register_coverage(server, project, build)

    def register_coverage(self, server, project, build):
        path = self.get_project_path(server, project)
        cover_path = join(path, 'cover')
        cover_file = join(cover_path, 'index.html')

        if exists(cover_file):
            with open(cover_file, 'r') as arq:
                log = arq.read()
                tab = BuildTab(name="Coverage", log=log, build=build)
                build.tabs.append(tab)