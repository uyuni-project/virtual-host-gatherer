
clean ::
	find . -type f -name '*~' | xargs rm

pylint ::
	find . -type f -name '*.py' | xargs pylint --rcfile ./pylint.rc


