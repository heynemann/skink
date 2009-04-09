# Makefile for Pyccuracy

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

.PHONY: help build compile test unit func acceptance run

help:
	@echo
	@echo "    skink Makefile v${file_version}"
	@echo "    usage: make <target>"
	@echo
	@echo "    targets:"
	@echo "    help             displays this help text"
	@echo "    build            compiles the code and runs all tests"
	@echo "    compile          compiles the python code"
	@echo "    test             runs all tests (unit, functional and acceptance)"
	@echo "    unit             runs all unit tests"
	@echo "    func             runs all functional tests"
	@echo "    acceptance       runs all acceptance tests"
	@echo "    run              runs the skink server"
	@echo
	@echo "    to run the tests with no coverage add nocoverage to the make script"
	@echo "    like this: make build nocoverage"
	@echo

# orchestrator targets

prepare_build: remove_build_dir create_build_dir

test: unit func acceptance

build: prepare_build compile test report_success

# action targets

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
	@echo ${nocoverage}
	@if [ -z "nocoverage" ];then @nosetests --verbose ${unit_tests_dir} >> ${unit_log_file} 2>> ${unit_log_file} else @nosetests --verbose --with-coverage --cover-package=skink ${unit_tests_dir} >> ${unit_log_file} 2>> ${unit_log_file}; fi

	@echo "============="
	@echo "Unit coverage"
	@echo "============="
	@cat build/unit.log | egrep '(Name)|(TOTAL)'
	@echo
	
func: compile
	@echo "Running functional tests..."
	@rm -f ${functional_log_file} >> /dev/null
	@nosetests --verbose --with-coverage --cover-package=skink ${functional_tests_dir} >> ${functional_log_file} 2>> ${functional_log_file}
	@echo "==================="
	@echo "Functional coverage"
	@echo "==================="
	@cat build/unit.log | egrep '(Name)|(TOTAL)'
	@echo
	
acceptance: compile
	@echo "Running acceptance tests..."
	@rm -f ${acceptance_log_file} >> /dev/null
	@nosetests ${acceptance_tests_dir} >> ${acceptance_log_file} 2>> ${acceptance_log_file}
	
run:
	@python skink/controllers/infra.py
	
