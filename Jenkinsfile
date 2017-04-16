pipeline {
  agent any
  stages {
    stage('init') {
      steps {
        echo 'init'
        sh '''docker info
docker version'''
      }
    }
    stage('build') {
      steps {
        sh 'docker build -t fileupload-webapp .'
      }
    }
    stage('deploy') {
      steps {
        sh '''docker tag fileupload-webapp:latest 780245226102.dkr.ecr.us-west-2.amazonaws.com/fileupload-webapp:latest
docker push 780245226102.dkr.ecr.us-west-2.amazonaws.com/fileupload-webapp:latest'''
      }
    }
  }
}