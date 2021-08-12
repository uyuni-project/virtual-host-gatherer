# Docker tests variables
DOCKER_CONTAINER_NAME = systemsmanagement/uyuni/master/docker/containers/uyuni-master-gatherer
DOCKER_REGISTRY       = registry.opensuse.org
DOCKER_RUN_EXPORT     = "PYTHONPATH=/gatherer/"
DOCKER_VOLUMES        = -v "$(CURDIR)/:/gatherer"

clean ::
	find . -type f -name '*~' | xargs rm

pylint ::
	pylint --rcfile ./.pylintrc lib/gatherer scripts/virtual-host-gatherer

pylint_in_docker ::
	pylint --rcfile ./.pylintrc --output-format=parseable --reports=y lib/gatherer scripts/virtual-host-gatherer | tee reports/pylint.log && exit $${PIPESTATUS[0]}

py3k ::
	pylint --py3k --rcfile ./.pylintrc lib/gatherer scripts/virtual-host-gatherer

py3k_in_docker ::
	pylint --py3k --rcfile ./.pylintrc --output-format=parseable --reports=y lib/gatherer scripts/virtual-host-gatherer | tee reports/py3k.log && exit $${PIPESTATUS[0]}

docker_pylint :: pull_container
	docker run --rm -e $(DOCKER_RUN_EXPORT) $(DOCKER_VOLUMES) $(DOCKER_REGISTRY)/$(DOCKER_CONTAINER_NAME) /bin/sh -c "cd /gatherer && make pylint_in_docker && make py3k_in_docker"

docker_shell ::
	docker run -t -i --rm -e $(DOCKER_RUN_EXPORT) $(DOCKER_VOLUMES) $(DOCKER_REGISTRY)/$(DOCKER_CONTAINER_NAME) /bin/bash

pull_container ::
	@echo "Pulling container"
	docker pull $(DOCKER_REGISTRY)/$(DOCKER_CONTAINER_NAME)
