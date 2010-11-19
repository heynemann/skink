bootstrap:
	@pip install -r requirements.txt

clean:
	@find . -name "*.pyc" -exec rm -f {} \;
	@rm -f .coverage
