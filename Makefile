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

.PHONY: help all compile test run_unit run_functional run_acceptance run

help:
	@echo
	@echo "    skink Makefile v${file_version}"
	@echo "    usage: make <target>"
	@echo
	@echo "    targets:"
	@echo "    help             displays this help text"
	@echo "    all              compiles the code and runs all tests"
	@echo "    createdb         drops the database and runs all migrations"
	@echo "    upgradedb        runs all migrations without dropping the db"
	@echo "    compile          compiles the python code"
	@echo "    test             runs all tests (unit, functional and acceptance)"
	@echo "    run_unit         runs all unit tests"
	@echo "    run_functional   runs all functional tests"
	@echo "    run_acceptance   runs all acceptance tests"
	@echo "    run              runs the skink server"
	@echo
	@echo "    to run the tests with no coverage add nocoverage to the make script"
	@echo "    like this: make build nocoverage"
	@echo

# orchestrator targets

prepare_build: clean create_build_dir

test: unit func acceptance

all: prepare_build compile test report_success

run_unit: prepare_build compile unit report_success
run_functional: prepare_build compile func report_success
run_acceptance: prepare_build compile acceptance report_success

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

unit: compile
	@echo "Running unit tests..."
	@rm -f ${unit_log_file} >> /dev/null
	@if [ "$(nocoverage)" = "true" ]; then nosetests -s --verbose ${unit_tests_dir} >> ${unit_log_file} 2>> ${unit_log_file}; else nosetests -s --verbose --with-coverage --cover-package=skink --cover-erase --cover-inclusive ${unit_tests_dir} >> ${unit_log_file} 2>> ${unit_log_file}; fi
	@echo "============="
	@echo "Unit coverage"
	@echo "============="
	@if [ "$(nocoverage)" != "true" ]; then cat ${unit_log_file} | egrep '(Name)|(TOTAL)'; fi
	@if [ "$(nocoverage)" = "true" ]; then echo 'Coverage Disabled.'; fi
	@echo
	
func: compile
	@echo "Running functional tests..."
	@rm -f ${functional_log_file} >> /dev/null
	@if [ "$(nocoverage)" = "true" ]; then nosetests -s --verbose ${functional_tests_dir} >> ${functional_log_file} 2>> ${functional_log_file}; else nosetests -s --verbose --with-coverage --cover-package=skink --cover-erase --cover-inclusive ${functional_tests_dir} >> ${functional_log_file} 2>> ${functional_log_file}; fi

	@echo "==================="
	@echo "Functional coverage"
	@echo "==================="
	@if [ "$(nocoverage)" != "true" ]; then cat ${functional_log_file} | egrep '(Name)|(TOTAL)'; fi
	@if [ "$(nocoverage)" = "true" ]; then echo 'Coverage Disabled.'; fi
	@echo
	
acceptance: compile
	@echo "Running acceptance tests..."
	@rm -f ${acceptance_log_file} >> /dev/null
	@nosetests ${acceptance_tests_dir} >> ${acceptance_log_file} 2>> ${acceptance_log_file}
	
run:
	@python skink/skink_console.py run
	
