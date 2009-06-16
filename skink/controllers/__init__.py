#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
from os.path import dirname, abspath, join, exists
root_path = abspath(join(dirname(__file__), "../../"))
sys.path.insert(0, root_path)

from skink.context import SkinkContext
from skink.imports import *
from skink.models import ProjectTab
from skink.repositories import ProjectRepository, PipelineRepository
from skink.services import BuildService
from skink.errors import *
from skink.controllers.filters import authenticated
from skink.plugins import PluginEvents
from skink.common import force_unicode
import template

class BaseController(object):
    def authenticated(self):
        return cherrypy.session.get('authenticated')

class IndexController(BaseController):
    @template.output("index.html")
    def index(self):
        repository = ProjectRepository()
        projects = repository.get_all()
        return template.render(authenticated=self.authenticated(), projects=projects)

    @template.output("login.html")
    def login(self, cancel=False, **data):
        return self.do_login(cancel, data)

    @template.output("login.html")
    def login_error(self, cancel=False, **data):
        data["login_error"] = "In order to do that you need to login. Please perform login below."
        return self.do_login(cancel, data)
        
    def do_login(self, cancel, data):
        if cherrypy.request.method == 'POST':
            ctx = SkinkContext.current()
            if cancel:
                raise cherrypy.HTTPRedirect('/')
            
            username = data["username"]
            password = data["password"]

            if username != ctx.username or password != ctx.password:
                return template.render(authenticated = self.authenticated, errors=["Invalid username or password!"])
            
            cherrypy.session['authenticated'] = True
            
            raise cherrypy.HTTPRedirect('/')

        errors = []
        if data.has_key("login_error"):
            errors.append(data["login_error"])
            
        return template.render(authenticated=self.authenticated(), errors=errors)

    def logoff(self):
        cherrypy.session['authenticated'] = False
        raise cherrypy.HTTPRedirect('/')

class ProjectController(BaseController):
    def __init__(self):
        self.repository = ProjectRepository()
        self.build_service = BuildService()
        
    @authenticated()
    @template.output("create_project.html")
    def new(self):
        return template.render(authenticated=self.authenticated(), project=None)

    @authenticated()
    @template.output("create_project.html")
    def edit(self, project_id):
        project = self.repository.get(project_id)
        return template.render(authenticated=self.authenticated(), project=project)

    def __process_tabs_for(self, data):
        tabs = None
        if data.has_key("additional_tab_name"):
            tab_names = [name for name in data["additional_tab_name"] if name != u'']
            tab_commands = [command for command in data["additional_tab_command"] if command != u'']
            tab_content_types = [content_type for content_type in data["additional_tab_content_type"] if content_type != u''][1:]

            if (len(tab_names) > len(tab_commands) or len(tab_names) > len(tab_content_types)):
                raise ValueError("The number of tabs, commands and content types MUST be the same.")

            tabs = []
            for tab_index in range(len(tab_names)):
                tab = ProjectTab(name=tab_names[tab_index], 
                                 command=tab_commands[tab_index], 
                                 content_type=tab_content_types[tab_index])
                tabs.append(tab)
        return tabs

    def __process_file_locators_for(self, data):
        locators = None
        if data.has_key("additional_file_locator"):
            locators = [locator for locator in data["additional_file_locator"] if locator != u'']
        return locators

    @authenticated()
    def create(self, name, build_script, scm_repository, monitor_changes=None, **data):
        project = self.repository.create(
                                name=name, 
                                build_script=build_script, 
                                scm_repository=scm_repository, 
                                monitor_changes=not monitor_changes is None,
                                tabs=self.__process_tabs_for(data),
                                file_locators=self.__process_file_locators_for(data))
        PluginEvents.on_project_created(project)
        raise cherrypy.HTTPRedirect('/')

    @authenticated()
    def update(self, project_id, name, build_script, scm_repository, monitor_changes=None, **data):
        project = self.repository.get(project_id)
        project.name = name
        project.build_script = build_script
        project.scm_repository = scm_repository
        project.monitor_changes = not monitor_changes is None
        self.repository.update(project, self.__process_tabs_for(data))
        PluginEvents.on_project_updated(project)
        raise cherrypy.HTTPRedirect('/')

    @authenticated()
    def delete(self, project_id):
        project = self.repository.get(project_id)
        self.repository.delete(project_id)
        self.build_service.delete_scm_repository(project)
        PluginEvents.on_project_deleted(project)
        raise cherrypy.HTTPRedirect('/')
    
    @authenticated()
    def build(self, project_id):
        print "Adding project %s to the queue" % project_id
        SkinkContext.current().build_queue.append(project_id)
        raise cherrypy.HTTPRedirect('/project/%s' % project_id)
            
    def build_status(self, **data):
        ctx = SkinkContext.current()
        projects = self.repository.get_all()
        projects_being_built = [int(project_id) for project_id in ctx.projects_being_built]
        result = {}
        for project in projects:
            if project.id in projects_being_built:
                result[project.id] = "BUILDING" 
            else:
                result[project.id] = (project.builds is not None and len(project.builds) > 0) and "BUILT" or "UNKNOWN"

        return "\n".join(["%s=%s" % (k,v) for k,v in result.items()])

    @template.output("project_details.html")
    def details(self, project_id):
        return self.render_details(project_id)

    @template.output("project_details.html")
    def build_details(self, project_id, build_id):
        return self.render_details(project_id, build_id)

    def build_tab_details(self, build_tab_id):
        return self.repository.get_build_tab_by_id(build_tab_id=build_tab_id).log

    def build_file_details(self, build_file_id):
        build_file = self.repository.get_build_file_by_id(build_file_id=build_file_id)
        response.headers['Content-Type'] = "application/x-download"
        response.headers["Content-Disposition"] = 'attachment; filename="%s"' % build_file.name
        response.headers["Accept-Ranges"] = "bytes"
        response.headers['Content-Length'] = len(build_file.content)
        response.body = build_file.content
        return response.body

    def get_all_status(self, **data):
        projects = self.repository.get_all()
        serialized_projects = []
        for project in projects:
            serialized_projects.append(project.to_dict())
        values = {}
        values["projects"] = serialized_projects
        
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return demjson.encode(values)

    def render_details(self, project_id, build_id = None):
        project = self.repository.get(project_id)
        if not build_id:
            build = project.builds and project.builds[0] or None
        else:
            build = project.get_build_by_id(int(build_id))
        build_log = ""
        if build and build.log:
            build_log = highlight(build.log, BashLexer(), HtmlFormatter())
        return template.render(authenticated=self.authenticated(), project=project, current_build=build, build_log=build_log)

class PipelineController(BaseController):
    def __init__(self):
        self.repository = PipelineRepository()
        
    @template.output("pipeline_index.html")
    def index(self):
        pipelines = self.repository.get_all()
        return template.render(authenticated=self.authenticated(), pipeline=None, pipelines=pipelines, errors=None)
    
    @authenticated()
    @template.output("pipeline_index.html") 
    def create(self, name, pipeline_definition):
        try:
            pipeline = self.repository.create(name, pipeline_definition)
            PluginEvents.on_pipeline_created(pipeline)
            raise cherrypy.HTTPRedirect('/pipeline')
        except (ProjectNotFoundError, CyclicalPipelineError), err:
            pipelines = self.repository.get_all()
            return template.render(authenticated=self.authenticated(), pipelines=pipelines, pipeline=None, errors=[err.message,]) | HTMLFormFiller(data=locals())

    @authenticated()
    @template.output("pipeline_index.html")
    def edit(self, pipeline_id):
        pipelines = self.repository.get_all()
        pipeline = self.repository.get(pipeline_id)
        return template.render(authenticated=self.authenticated(), pipeline=pipeline, pipelines=pipelines, errors=None)

    @authenticated()
    @template.output("pipeline_index.html") 
    def update(self, pipeline_id, name, pipeline_definition):
        pipeline = self.repository.get(int(pipeline_id))
        try:
            pipeline = self.repository.update(pipeline.id, name, pipeline_definition)
            PluginEvents.on_pipeline_updated(pipeline)
            raise cherrypy.HTTPRedirect('/pipeline')
        except (ProjectNotFoundError, CyclicalPipelineError), err:
            pipelines = self.repository.get_all()
            return template.render(authenticated=self.authenticated(), pipelines=pipelines, pipeline=pipeline, errors=[err.message,]) | HTMLFormFiller(data=locals())
    
    @authenticated()
    def delete(self, pipeline_id):
        pipeline = self.repository.get(pipeline_id)
        self.repository.delete(pipeline_id)
        PluginEvents.on_pipeline_deleted(pipeline)
        raise cherrypy.HTTPRedirect('/pipeline')
