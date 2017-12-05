pipeline {
  /* See https://groups.google.com/forum/#!topic/jenkinsci-users/y_IOIxXb4T8 */
  /* agent { label 'docker' } */
  agent any
  environment {
    DOCKER_USERNAME = credentials('DOCKER_USERNAME')
    DOCKER_PASSWORD = credentials('DOCKER_PASSWORD')
  }
  stages {
    stage('Build') {
      steps {
        sh '''env
docker info'''
      }
    }
    stage('Test') {
      steps {
        sh '''env
docker info'''
      }
    }
  }
}