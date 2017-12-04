pipeline {
  agent {
    docker {
      image 'docker:17.05.0-ce-git'
    }
    
  }
  stages {
    stage('init') {
      steps {
        sh '''apk update
apk add make bash'''
      }
    }
    stage('build') {
      steps {
        sh 'make NOCACHE=true docker-build'
      }
    }
    stage('test') {
      steps {
        sh 'make test-docker'
      }
    }
    stage('push') {
      steps {
        sh '''docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
make docker-push IMAGE_NAME="${DOCKER_USERNAME}/fileupload-webapp:$(git rev-parse --short HEAD)"'''
      }
    }
  }
  environment {
    DOCKER_USERNAME = 'credentials(\'DOCKER_USERNAME\')'
    DOCKER_PASSWORD = 'credentials(\'DOCKER_PASSWORD\')'
  }
}