#!/bin/bash -ex

# TODO get gitlab pipeline status
cat > status.json <<
{
  "state": "success",
  "target_url": "${CI_PROJECT_URL}/pipelines/${CI_PIPELINE_ID}",
  "description": "The pipeline succeeded!",
  "context": "internal/gitlab-pipeline"
}
EOF

curl \
  -u ${GITHUB_USERNAME}:${GITHUB_TOKEN} \
  -X POST \
  -H "application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  --data @status.json \
  https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO_NAME}/statuses/${CI_COMMIT_SHA}


