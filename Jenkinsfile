pipeline {
  agent any
  stages {
    stage('init') {
      steps {
        sh '''docker info
docker version
git rev-parse --short HEAD > latest_commit
echo "latest commit is $(cat latest_commit)"'''
      }
    }
    stage('build') {
      steps {
        sh '''latest_commit=$(cat latest_commit)
echo "last commit is ${last_commit}"

registry_url="780245226102.dkr.ecr.us-west-2.amazonaws.com"

docker build -t fileupload-webapp:${last_commit} .
docker tag fileupload-webapp:${last_commit} ${registry_url}/fileupload-webapp:${last_commit}
docker push ${registry_url}/fileupload-webapp:${last_commit}'''
      }
    }
    stage('deploy') {
      steps {
        sh '''latest_commit=$(cat latest_commit)
echo "last commit is ${last_commit}"

registry_url="780245226102.dkr.ecr.us-west-2.amazonaws.com"

# update the ecs task definition
# create a new revision for the new image
aws ecs register-task-definition --cli-input-json << EOF
{
    "family": "fileupload-webapp",
    "containerDefinitions": [
        {
            "name": "fileupload-webapp",
            "image": "${registry_url}/fileupload-webapp:${latest_commit}",
            "cpu": 100,
            "memory": 256,
            "portMappings": [
                    {
                        "protocol": "tcp",
                        "containerPort": 5000,
                        "hostPort": 0
                    }
            ],
            "essential": true
        }
    ]
}
EOF

# find the revision just created
task_definition=$(aws ecs list-task-definitions | jq '.taskDefinitionArns[-1]')

# find the service name for fileupload-service
service_name=$(aws ecs list-services | jq '.serviceArns[] | select(contains("fileupload-service"))')

# update the service to use the new revision of the task definition
aws ecs update-service --service ${service_name} --task-definition ${task_definition}'''
      }
    }
  }
}