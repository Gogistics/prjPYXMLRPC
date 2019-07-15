#!/usr/local/bin/bash
# Author:
#   Alan Tai
# Program:
#   Spin up the control system
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
# build Docker images and push to docker registry

# 
docker build -t alantai/isi_control_system:0.0.0 \
  -f ./infra/Dockerfiles/Dockerfile.control_system .

docker run -d --name isi_control_system \
  --network $DOCKER_NETWORK_ROBOT_SYSTEM \
  --ip $CONTROLLER_IP \
  -e CONTROLLER_ID=$CONTROLLER_ID \
  -e CONTROLLER_IP=$CONTROLLER_IP \
  -e CONTROLLER_PORT=$CONTROLLER_PORT \
  -e MONGO_IP=$MONGO_IP \
  -e MONGO_PORT=$MONGO_PORT \
  -e MONGO_DB=$MONGO_CONTROL_SYSTEM_DB \
  -e MONGO_COLLECTION_LOGS=$MONGO_CONTROL_SYSTEM_COLLECTION_LOGS \
  -e REDIS_IP=$REDIS_IP \
  -e REDIS_PORT=$REDIS_PORT \
  -e REDIS_DB=$REDIS_DB \
  -e POSTGRES_IP=$POSTGRES_IP \
  -e POSTGRES_PORT=$POSTGRES_PORT \
  -e POSTGRES_DB=$POSTGRES_DB \
  -e POSTGRES_USER=$POSTGRES_USER \
  --log-opt mode=non-blocking \
  --log-opt max-buffer-size=4m \
  --log-opt max-size=100m \
  --log-opt max-file=5 \
  alantai/isi_control_system:0.0.0

set -e

# docker logout $DOCKER_REGISTRY_ACCOUNT
