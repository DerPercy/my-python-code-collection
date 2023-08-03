init:
	pip install -r requirements.txt

test:
	py.test -o log_cli=true -o log_cli_level=DEBUG tests