# Makefile for Pyccuracy
SHELL := /bin/bash

# Internal variables.
file_version=0.1.0
root_dir=.
build_dir=${root_dir}/build
src_dir=${root_dir}/skink

tests_dir=${root_dir}/tests
unit_tests_dir=${tests_dir}/unit
functional_tests_dir=${tests_dir}/functional
acceptance_tests_dir=${tests_dir}/acceptance

compile_log_file=${build_dir}/compile.log
unit_log_file=${build_dir}/unit.log
functional_log_file=${build_dir}/functional.log
acceptance_log_file=${build_dir}/acceptance.log
nocoverage=false

# orchestrator targets

prepare_build: clean create_build_dir

test: prepare_build compile run_unit run_functional run_acceptance

all: prepare_build compile test report_success

unit: prepare_build compile run_unit report_success
functional: prepare_build compile run_functional report_success
acceptance: prepare_build compile run_acceptance report_success

clean: remove_build_dir

kill:
	-@ps aux | egrep skink | egrep -v egrep | awk {'print $$2'} | xargs kill -9
	@echo "Skink killed!"

# action targets

createdb:
	@skink/skink_console.py createdb

upgradedb:
	@skink/skink_console.py upgradedb

report_success:
	@echo "Build succeeded!"

remove_build_dir:
	@rm -fr ${build_dir}

create_build_dir:
	@mkdir -p ${build_dir}

compile:
	@echo "Compiling source code..."
	@rm -f ${compile_log_file} >> /dev/null
	@rm -f -r ${src_dir}/*.pyc >> /dev/null
	@python -m compileall ${src_dir} >> ${compile_log_file} 2>> ${compile_log_file}

run_unit: compile
	@echo "Running run_unit tests..."
	@rm -f ${unit_log_file} >> /dev/null
	@if [ "$(nocoverage)" = "true" ]; then nosetests -d -s --verbose ${unit_tests_dir}; else nosetests -d -s --verbose --with-coverage --cover-package=skink.src --cover-package=skink.lib.ion --cover-erase --cover-inclusive ${unit_tests_dir}; fi

run_functional: compile
	@echo "Running run_functional tests..."
	@rm -f ${functional_log_file} >> /dev/null
	@if [ "$(nocoverage)" = "true" ]; then nosetests -s --verbose ${functional_tests_dir}; else nosetests -s --verbose --with-coverage --cover-package=skink.src --cover-package=skink.lib.ion --cover-erase --cover-inclusive ${functional_tests_dir}; fi

run_acceptance: compile
	@echo "Running run_acceptance tests..."
	@rm -f ${acceptance_log_file} >> /dev/null
	@nosetests ${acceptance_tests_dir}

documentation:
	cd docs && make html
	firefox `pwd`/docs/build/html/index.html &

run:
	@python skink/skink_console.py run
	
