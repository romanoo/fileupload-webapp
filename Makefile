SHELL := /bin/bash
PROJECT_DIR = $(shell pwd)
IMAGE_NAME ?= rgrecour/fileupload-webapp:latest

.PHONY: clean docker-build docker-push

default: docker-build

docker-build:
	if [ ! -z "$${http_proxy}" ] ; then \
		DOCKER_BUILD_ARGS="--build-arg http_proxy=http://$${http_proxy##*://}" ; \
	fi ; \
	if [ ! -z "$${https_proxy}" ] ; then \
		DOCKER_BUILD_ARGS="$${DOCKER_BUILD_ARGS} --build-arg https_proxy=http://$${https_proxy##*://}" ; \
	fi ; \
	if [ ! -z "$${NO_PROXY}}" ] ; then \
		DOCKER_BUILD_ARGS="$${DOCKER_BUILD_ARGS} --build-arg NO_PROXY=$${NO_PROXY}" ; \
	fi ; \
	if [ "$${NOCACHE}" = "true" ] ; then \
		DOCKER_BUILD_ARGS="$${DOCKER_BUILD_ARGS} --no-cache" ; \
	fi ; \
	docker build $${DOCKER_BUILD_ARGS} -t $(IMAGE_NAME) $(PROJECT_DIR)

docker-push:
	docker push $(IMAGE_NAME)

clean:
	docker rmi -f $(IMAGE_NAME) || true