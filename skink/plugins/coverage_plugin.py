#!/usr/bin/env python
# -*- coding:utf-8 -*-

from os.path import join, abspath, dirname, exists

from skink.models import Project, Pipeline, PipelineItem
from skink.plugins import Plugin, Guard
from skink.context import SkinkContext

class CoveragePlugin (Plugin):
    section = "CoveragePlugin" 
    config_keys = []
    
    def __init__(self, configuration=None):
        super(CoveragePlugin, self).__init__(configuration)

        root_path = abspath(join(dirname(__file__), "../../"))

        self.base_path = join(root_path, SkinkContext.current().build_path)

    def try_to_import_coverage(self):
        from coverage import __version__
        if int(version[:3].replace('.')) < 32:
            print "You have an out-of-date version of coverage. Please get a new version in order to use Skink's coverage plugin."
            self.report_coverage = False
        else:
            self.report_coverage = True
            from coverage import coverage

    def on_build_successful(self, project, build):
        if not self.report_coverage:
            return

        cov = coverage()
        project_name = self.fix_name(project.name)
        repository_path = join(self.base_dir, project_name)
        coverage_file = join(repository_path, '.coverage')
        
        if not exists(coverage_file):
            print "No .coverage file found for project %s under path %s" % (project.name, repository_path)
        
        xml_report_path = join(repository_path, 'coverage.xml')
        
        cov.load(coverage_file)
        cov.xml_report(outfile=xml_report_path)
        
        save_xml_report_data_for(xml_report_path)
    
    def save_xml_report_data_for(self, xml_report_path):
        pass

    def fix_name(self, name):
        return name.strip().replace(" ", "")
