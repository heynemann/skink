format='html'

test: unit functional acceptance

unit:
	@specloud --nocapture --where=tests/unit --with-coverage --cover-package=skink --cover-erase

functional:
	@specloud --nocapture --where=tests/functional --with-coverage --cover-package=skink --cover-erase

acceptance:
	@lettuce

documentation:
	@cd docs && make $(format)

bootstrap:
	@pip install -r requirements.txt

clean:
	@find . -name "*.pyc" -exec rm -f {} \;
	@rm -f .coverage
