SHELL := /bin/bash
PROJECT_DIR = $(shell pwd)
LOCAL_IMAGE_NAME = fileupload-webapp
THIS_FILE := $(lastword $(MAKEFILE_LIST))
TEST_ARGS ?=

.PHONY: clean docker-build docker-push docker-run docker-rm docker-rmi run test test-docker

default: docker-build

run:
	python3 src/main/app.py --debug

test:
	python3 src/test/app_test.py $(TEST_ARGS)
	bash src/test/curl_test.sh $(TEST_ARGS)

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
	docker build $${DOCKER_BUILD_ARGS} -t $(LOCAL_IMAGE_NAME) $(PROJECT_DIR)

docker-push:
ifndef IMAGE_NAME
	$(error "IMAGE_NAME parameter required, invoke run with IMAGE_NAME=XXX")
endif
	docker tag fileupload-webapp $(IMAGE_NAME)
	docker push $(IMAGE_NAME)

docker-run:
	docker run -d -p 5000:5000 --name $(LOCAL_IMAGE_NAME) $(LOCAL_IMAGE_NAME)
	docker run --rm --link $(LOCAL_IMAGE_NAME) appropriate/curl \
		curl --noproxy '*' --retry 10 --retry-delay 5 http://$(LOCAL_IMAGE_NAME):5000 \
		> /dev/null 2>&1

docker-rm:
	docker rm -f $(LOCAL_IMAGE_NAME) || true

docker-rmi:
	docker rmi -f $(LOCAL_IMAGE_NAME) || true

test-docker: docker-run
	if [ ! -z "$${http_proxy}" ] ; then \
		DOCKER_RUN_ARGS="-e http_proxy=http://$${http_proxy##*://}" ; \
	fi ; \
	if [ ! -z "$${https_proxy}" ] ; then \
		DOCKER_RUN_ARGS="$${DOCKER_RUN_ARGS} -e https_proxy=http://$${https_proxy##*://}" ; \
	fi ; \
	if [ ! -z "$${NO_PROXY}}" ] ; then \
		DOCKER_RUN_ARGS="$${DOCKER_RUN_ARGS} -e NO_PROXY=$${NO_PROXY}" ; \
	fi ; \
	docker run $${DOCKER_RUN_ARGS} --rm --link $(LOCAL_IMAGE_NAME) $(LOCAL_IMAGE_NAME) \
		sh -c 'apk update ; apk add curl bash make ; make test TEST_ARGS=--url=http://$(LOCAL_IMAGE_NAME):5000'
	@$(MAKE) -f $(THIS_FILE) docker-rm

clean: docker-rm docker-rmi