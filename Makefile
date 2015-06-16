# Docker tests variables
DOCKER_CONTAINER_NAME = suma-head-gatherer
DOCKER_REGISTRY       = ${DOCKER_REGISTRY}
DOCKER_RUN_EXPORT     = "PYTHONPATH=/gatherer/"
DOCKER_VOLUMES        = -v "$(CURDIR)/:/gatherer"

clean ::
	find . -type f -name '*~' | xargs rm

pylint ::
	pylint --rcfile ./.pylintrc lib/gatherer scripts/gatherer

pylint_in_docker ::
	pylint --rcfile ./.pylintrc --output-format=parseable --reports=y lib/gatherer scripts/gatherer > reports/pylint.log ||:

py3k ::
	pylint --py3k --rcfile ./.pylintrc lib/gatherer scripts/gatherer

py3k_in_docker ::
	pylint --py3k --rcfile ./.pylintrc --output-format=parseable --reports=y lib/gatherer scripts/gatherer > reports/py3k.log ||:

docker_pylint ::
	docker run --rm -e $(DOCKER_RUN_EXPORT) $(DOCKER_VOLUMES) $(DOCKER_REGISTRY)/$(DOCKER_CONTAINER_NAME) /bin/sh -c "cd /gatherer; make pylint_in_docker; make py3k_in_docker"
