
clean ::
	find . -type f -name '*~' | xargs rm

pylint ::
	find . -type f -name '*.py' | xargs pylint --rcfile ./pylint.rc
	PYTHONPATH=./lib pylint --rcfile ./pylint.rc scripts/gatherer

py3k ::
	find . -type f -name '*.py' | xargs pylint --py3k --rcfile ./pylint.rc
	PYTHONPATH=./lib pylint --py3k --rcfile ./pylint.rc scripts/gatherer
