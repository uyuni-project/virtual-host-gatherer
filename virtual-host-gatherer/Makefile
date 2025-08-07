# Docker tests variables
DOCKER_CONTAINER_NAME = systemsmanagement/uyuni/master/docker/containers/uyuni-master-gatherer
DOCKER_REGISTRY       = registry.opensuse.org
DOCKER_RUN_EXPORT     = "PYTHONPATH=/gatherer/"
DOCKER_VOLUMES        = -v "$(CURDIR)/:/gatherer"

# We ONLY run pylint on uyuni-master-python image.
# We do not run it for SUSE Multi-Linux Manager images.
DOCKER_PYLINT_CONTAINER = systemsmanagement/uyuni/master/docker/containers_tw/uyuni-master-python
DOCKER_PYLINT_REGISTRY = registry.opensuse.org

clean ::
	find . -type f -name '*~' | xargs rm

pylint ::
	pylint --rcfile ./.pylintrc lib/gatherer scripts/virtual-host-gatherer

tests ::
	echo "No tests for virtual-host-gatherer"

tests_in_docker ::
	echo "No tests for virtual-host-gatherer"

docker_pylint :: pull_container_pylint
	docker run --rm -e $(DOCKER_RUN_EXPORT) $(DOCKER_VOLUMES) $(DOCKER_PYLINT_REGISTRY)/$(DOCKER_PYLINT_CONTAINER) /bin/sh -c \
	"cd /gatherer/; pylint --rcfile ./.pylintrc --output-format=parseable --reports=y lib/gatherer scripts/virtual-host-gatherer | tee reports/pylint.log && exit \$${PIPESTATUS[0]}"

docker_tests :: pull_container
	docker run --rm -e $(DOCKER_RUN_EXPORT) $(DOCKER_VOLUMES) $(DOCKER_REGISTRY)/$(DOCKER_CONTAINER_NAME) /bin/sh -c "make tests_in_docker"

docker_shell_pylint ::
	docker run -t -i --rm -e $(DOCKER_RUN_EXPORT) $(DOCKER_VOLUMES) $(DOCKER_PYLINT_REGISTRY)/$(DOCKER_PYLINT_CONTAINER) /bin/bash

docker_shell ::
	docker run -t -i --rm -e $(DOCKER_RUN_EXPORT) $(DOCKER_VOLUMES) $(DOCKER_REGISTRY)/$(DOCKER_CONTAINER_NAME) /bin/bash

pull_container ::
	@echo "Pulling container"
	docker pull $(DOCKER_REGISTRY)/$(DOCKER_CONTAINER_NAME)

pull_container_pylint ::
	@echo "Pulling pylint container"
	docker pull $(DOCKER_PYLINT_REGISTRY)/$(DOCKER_PYLINT_CONTAINER)
