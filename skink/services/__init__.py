#!/usr/bin/env python
#-*- coding:utf-8 -*-
from datetime import datetime
import sys
from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.imports import *
from skink.models import Build, BuildTab
from skink.repositories import ProjectRepository, PipelineRepository
from skink.services.scm import GitRepository, ScmResult
from skink.services.executers import ShellExecuter
from skink.context import SkinkContext
from skink.plugins import PluginEvents

class BuildService(object):
    Success = u"SUCCESS"
    Failure = u"FAILURE"
    
    def default_flush(self):
        elixir.session.commit()
        elixir.session.flush()
    
    def __init__(self, repository=None, pipeline_repository=None, scm=None, executer=None, flush_action=None, base_path=join(root_path, SkinkContext.current().build_path)):
        self.repository = repository
        if not repository:
            self.repository = ProjectRepository()

        self.pipeline_repository = pipeline_repository
        if not pipeline_repository:
            self.pipeline_repository = PipelineRepository()

        self.scm = scm
        if not scm:
            self.scm = GitRepository(base_path)

        self.executer = executer
        if not executer:
            self.executer = ShellExecuter()    

        self.flush_action = flush_action
        if not flush_action:
            self.flush_action = self.default_flush
        
        self.base_path = base_path

    def build_project(self, project_id):
        ctx = SkinkContext.current()
        
        log = ["Build started at %s" % datetime.now()]

        status = BuildService.Failure
        scm_status = ScmResult.Failed
        project = self.repository.get(project_id)
        PluginEvents.on_before_build(project)
        ctx.projects_being_built.append(project_id)
        last_build_number = project.get_last_build_number()

        build = Build()
        build.date = datetime.now()
        build.status = status
        build.scm_status = scm_status
        build.log = ""
        build.project = project
        
        scm_creation_result = self.scm.create_or_update(project)
        build.scm_status = scm_creation_result.status
        if scm_creation_result.status == ScmResult.Failed:
            log.append(scm_creation_result.log)
            status = BuildService.Failure
        else:
            log.append("Downloaded code from %s (%s)" % (project.scm_repository, scm_creation_result.status))
            
            execute_result = self.executer.execute(project.build_script, scm_creation_result.repository_path)
            log.append("Executed %s" % project.build_script)
            log.append("Exit Code: %s" % execute_result.exit_code)
            log.append("Run Log:")
            log.append(execute_result.run_log)

            status = execute_result.exit_code == 0 and BuildService.Success or BuildService.Failure

        for command in project.tabs:
            build_tab = BuildTab(name=command.name, command=command.command, build=build)
            result = self.executer.execute(command.command, scm_creation_result.repository_path)
            build_tab.log = result.run_log

        build.number = last_build_number + 1
        build.status = status
        build.log = "\n".join(log)
        build.commit_number = self.force_unicode(scm_creation_result.last_commit["commit_number"])
        build.commit_author = self.force_unicode(scm_creation_result.last_commit["author"])
        build.commit_committer = self.force_unicode(scm_creation_result.last_commit["committer"])
        build.commit_author_date = scm_creation_result.last_commit["author_date"]
        build.commit_committer_date = scm_creation_result.last_commit["committer_date"]
        build.commit_text = self.force_unicode(scm_creation_result.last_commit["subject"])
        
        self.repository.update(project, None)
        
        self.flush_action()
        
        ctx.projects_being_built.remove(project_id)

        if (build.status == BuildService.Success):
            PluginEvents.on_build_successful(project, build)
            self.process_pipelines_for(project)
        else:
            PluginEvents.on_build_failed(project, build)
        
        return build
    
    def force_unicode(self, s, encoding='utf-8', errors='strict'):
        print "Decoding %s with encoding %s" % (s, encoding)
        if not isinstance(s, basestring,):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                try:
                    s = unicode(str(s), encoding, errors)
                except UnicodeEncodeError:
                    if not isinstance(s, Exception):
                        raise
                    s = ' '.join([self.force_unicode(arg, encoding, errors) for arg in s])
        elif not isinstance(s, unicode):
            s = s.decode(encoding, errors)

        return s
    
    def delete_scm_repository(self, project):
        self.scm.remove_repository(project)
        
    def process_pipelines_for(self, project):
        pipelines = self.pipeline_repository.get_all_pipelines_for(project)
        for pipeline in pipelines:
            for i in range(len(pipeline.items)):
                if i < len(pipeline.items) - 1:
                    if pipeline.items[i].project.id == project.id:
                        print "Adding project %d to the queue because it's in the same pipeline as project %s" % (pipeline.items[i+1].project.id, pipeline.items[i].project.name)
                        SkinkContext.current().build_queue.append(pipeline.items[i+1].project.id)
