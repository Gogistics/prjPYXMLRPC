#!/bin/bash
#
# Author:
#   Alan Tai
# Program:
#   Create Docker images for running applications and push Docker registry if needed (WIP)
# Date:
#   7/13/2019

set -e

# export variables
source $(pwd)/scripts/env_variables
CWD=$(pwd)

finish() {
  local existcode=$?
  cd $CWD
  exit $existcode
}

trap "finish" INT TERM

# login registry
docker login -u $DOCKER_REGISTRY_USER_NAME -p $DOCKER_REGISTRY_PWD $DOCKER_REGISTRY_ACCOUNT

set +e

# build Docker images and push to docker registry
set -e

docker logout $DOCKER_REGISTRY_ACCOUNT
