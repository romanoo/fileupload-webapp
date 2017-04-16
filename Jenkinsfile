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
        sh 'echo "docker tag..."'
      }
    }
  }
}
