#!/usr/local/bin/bash
# Author:
#   Alan Tai
# Program:
#   Spin up the subsystems
# Date:
#   7/13/2019
# Note: Install Bash 4+ to create associate arrary

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

# build base img
docker build -t alantai/isi_subsystem:0.0.0 \
  -f ./infra/Dockerfiles/Dockerfile.subsystem .

declare -A subsystem0=(
  [container_name]='isi_subsystem_1'
  [id]='SUBSYS-1000'
  [ip]='172.99.1.1'
)

declare -A subsystem1=(
  [container_name]='isi_subsystem_2'
  [id]='SUBSYS-2000'
  [ip]='172.99.1.2'
)

declare -n subsystem

for subsystem in ${!subsystem@}; do
  docker run -d --name ${subsystem[container_name]} \
    --network $DOCKER_NETWORK_ROBOT_SYSTEM \
    --ip ${subsystem[ip]} \
    -e SUBSYS_ID=${subsystem[id]} \
    -e EXPOSE_PORT=$SUBSYSTEM_EXPOSE_PORT \
    -e CONTROLLER_IP=$CONTROLLER_IP \
    -e CONTROLLER_PORT=$CONTROLLER_PORT \
    -e MONGO_IP=$MONGO_IP \
    -e MONGO_PORT=$MONGO_PORT \
    -e MONGO_DB=$MONGO_SUBSYSTEM_DB \
    -e MONGO_COLLECTION_LOGS=$MONGO_SUBSYSTEM_COLLECTION_LOGS \
    --log-opt mode=non-blocking \
    --log-opt max-buffer-size=4m \
    --log-opt max-size=100m \
    --log-opt max-file=5 \
    alantai/isi_subsystem:0.0.0
done

set -e

# docker logout $DOCKER_REGISTRY_ACCOUNT
