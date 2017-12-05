pipeline {
  // See https://groups.google.com/forum/#!topic/jenkinsci-users/y_IOIxXb4T8
  agent any
  // XXX should use a node with a label 'docker'
  // agent { label 'docker' }
  environment {
    DOCKER_USERNAME = credentials('DOCKER_USERNAME')
    DOCKER_PASSWORD = credentials('DOCKER_PASSWORD')
    // the following variable is used by the Makefile for the local image name
    // making it unique to avoid conflicts with concurrent runs
    LOCAL_IMAGE_NAME = 'fileupload-webapp:${BUILD_TAG}'
  }
  stages {
    stage('Init') {
      // XXX assuming alpine
      steps {
        sh '''if [ ! -z "${http_proxy}" ] ; then  export http_proxy="http://${http_proxy##*://}" ; fi
if [ ! -z "${HTTP_PROXY}" ] ; then  export HTTP_PROXY="http://${HTTP_PROXY##*://}" ; fi
apk update
apk add bash make'''
      }
    }
    stage('Build') {
      steps {
        sh 'make NOCACHE=true clean docker-build'
      }
    }
    stage('Test') {
      steps {
        sh 'make test-docker'
      }
    }
    stage('Push') {
      steps {
        sh '''docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
SHORT_COMMIT_ID=$(git rev-parse --short HEAD)
export IMAGE_NAME="${DOCKER_USERNAME}/fileupload-webapp:b${BUILD_ID}-${SHORT_COMMIT_ID}"
make docker-push'''
      }
    }
  }
}