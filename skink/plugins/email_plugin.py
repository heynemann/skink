from skink.models import Project, Pipeline, PipelineItem
from . import BasePlugin
from hamcrest import *

class EmailPlugin (BasePlugin):

    def __init__(self,configuration):
        self.configuration = Dict(configuration)


