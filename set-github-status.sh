#!/bin/bash -ex

readonly SCRIPT_NAME=$(basename ${0})
log_msg(){
    if [ ${#@} -eq 0 ] ; then echo "log_msg - missing arguments: msg ..." ; return 1 ; fi
    printf "\n### [`TZ=PST8PDT date +"%b %d %Y %T"`] [ ${SCRIPT_NAME} ] ${*} ###\n"
}

# TODO add cmd usage and params

if [ "${1}" = "pending" ] ; then
  STATE="pending"
  DESCRIPTION="Internal Gitlab pipeline created"
else
  log_msg "[INFO] - Retrieving pipeline state"

  # parse CI_PROJECT_URL
  CI_PROJECT_URL_FIELDS=($(echo "${CI_PROJECT_URL}" | \
    awk '{split($0, arr, /[\/\@:]*/); for (x in arr) { print arr[x] }}'))

  # derive GITLAB_HOST and GITLAB_API_URL from CI_PROJECT_URL
  GITLAB_HOST=${CI_PROJECT_URL_FIELDS[1]}
  GITLAB_API_URL="${CI_PROJECT_URL_FIELDS[3]}://${GITLAB_HOST}/api/v4"

  PIPELINE_STATE_HTTP_CODE=$(curl -k --noproxy ${GITLAB_HOST} \
        --silent \
        --write-out "%{http_code}\n" \
        -o gitlab-pipeline-jobs.json \
        --header "PRIVATE-TOKEN: ${PRIVATE_TOKEN}" \
        "${GITLAB_API_URL}/projects/${PROJECT_ID}")

  if [ "${PIPELINE_STATE_HTTP_CODE}" != "200" ] ; then
    log_msg "[ERROR] - Unexpected http_code (${PIPELINE_STATE_HTTP_CODE})" >&2
    exit 1
  fi

  IS_SUCCESS=$(cat gitlab-pipeline-jobs.json | \
    jq "[ .[] | select(.name != \"${CI_JOB_NAME}\") ] | all(.status == \"success\")")

  if ${IS_SUCCESS} ; then
    STATE="failure"
    DESCRIPTION="Internal Gitlab pipeline failed"
  else
    STATE="success"
    DESCRIPTION="Internal Gitlab pipeline passed"
  fi
fi

log_msg "[INFO] - Reporting pipeline state(${STATE})"

cat > status.json << EOF
  {
    "state": "${STATE}",
    "target_url": "${CI_PROJECT_URL}/pipelines/${CI_PIPELINE_ID}",
    "description": "${DESCRIPTION}",
    "context": "internal/gitlab-pipeline"
  }
EOF

REPORT_STATE_HTTP_CODE=$(curl \
  -u ${GITHUB_USERNAME}:${GITHUB_TOKEN} \
  --silent \
  --write-out "%{http_code}\n" \
  -X POST \
  -H "application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  -o github-status.json \
  --data @status.json \
  https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO_NAME}/statuses/${CI_COMMIT_SHA})

if [ "${REPORT_STATE_HTTP_CODE}" != "201" ] ; then
  log_msg "[ERROR] - Unexpected http_code (${REPORT_STATE_HTTP_CODE})" >&2
  exit 1
fi
