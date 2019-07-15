#!/usr/local/bin/bash
# Author:
#   Alan Tai
# Program:
#   Configure networks for the control system and the subsystems
# Date:
#   7/13/2019

set -e

# export variables
source $(pwd)/infra/scripts/env_variables
CWD=$(pwd)

finish() {
  local existcode=$?
  cd $CWD
  exit $existcode
}

trap "finish" INT TERM

# login registry
# docker login -u $DOCKER_REGISTRY_USER_NAME -p $DOCKER_REGISTRY_PWD $DOCKER_REGISTRY_ACCOUNT

set +e

# create a private subnet
NETWORK_INSPECTION=$(docker network inspect "$DOCKER_NETWORK_ROBOT_SYSTEM")
EXITCODE_NETWORK_INSPECTION=$?
[[ $EXITCODE_NETWORK_INSPECTION -ne 0 ]] || (echo "Network, $DOCKER_NETWORK_ROBOT_SYSTEM, exists and will be reset" && docker network rm $DOCKER_NETWORK_ROBOT_SYSTEM)

docker network create \
  --driver=$DOCKER_NETWORK_ROBOT_SYSTEM_DRIVER \
  --gateway=$DOCKER_NETWORK_ROBOT_SYSTEM_GATEWAY \
  --subnet=$DOCKER_NETWORK_ROBOT_SYSTEM_SUBNET \
  $DOCKER_NETWORK_ROBOT_SYSTEM

set -e

# docker logout $DOCKER_REGISTRY_ACCOUNT
