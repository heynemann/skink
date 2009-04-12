from skink.models import Project, Pipeline, PipelineItem
from . import BasePlugin
from hamcrest import *

class EmailPlugin (BasePlugin):

    def __init__(self,configuration):
        Guard.against_empty(configuration.get('smtp_host',None))
        
        self.configuration = Dict(configuration)


