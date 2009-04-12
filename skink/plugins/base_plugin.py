class BasePlugin (object):
    def OnProjectCreated(self, project):
        pass

    def OnProjectUpdated(self, project):
        pass

    def OnProjectDeleted(self, project):
        pass

    def OnPipelineCreated(self, pipeline):
        pass

    def OnPipelineUpdated(self, pipeline):
        pass

    def OnPipelineDeleted(self, pipeline):
        pass

    def OnBeforeBuild(self, project):
        pass

    def OnBuildSuccessful(self, project, build):
        pass

    def OnBuildFailed(self, project, build):
        pass

