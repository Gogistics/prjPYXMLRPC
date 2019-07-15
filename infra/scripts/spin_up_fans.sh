#!/usr/local/bin/bash
# Author:
#   Alan Tai
# Program:
#   Spin up the fan systems
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
docker build -t alantai/isi_fan:0.0.0 \
  -f ./infra/Dockerfiles/Dockerfile.fan .

declare -A fan0=(
  [container_name]='isi_fan_1'
  [id]='FAN-1000'
  [ip]='172.99.2.1'
)
declare -A fan1=(
  [container_name]='isi_fan_2'
  [id]='FAN-2000'
  [ip]='172.99.2.2'
)
declare -A fan2=(
  [container_name]='isi_fan_3'
  [id]='FAN-3000'
  [ip]='172.99.2.3'
)

declare -n fan

for fan in ${!fan@}; do
  docker run -d --name ${fan[container_name]} \
    --network $DOCKER_NETWORK_ROBOT_SYSTEM \
    --ip ${fan[ip]} \
    -e FAN_ID=${fan[id]} \
    -e EXPOSE_PORT=$FAN_EXPOSE_PORT \
    -e CONTROLLER_IP=$CONTROLLER_IP \
    -e CONTROLLER_PORT=$CONTROLLER_PORT \
    -e MONGO_IP=$MONGO_IP \
    -e MONGO_PORT=$MONGO_PORT \
    -e MONGO_DB=$MONGO_FAN_DB \
    -e MONGO_COLLECTION_LOGS=$MONGO_FAN_COLLECTION_LOGS \
    --log-opt mode=non-blocking \
    --log-opt max-buffer-size=4m \
    --log-opt max-size=100m \
    --log-opt max-file=5 \
    alantai/isi_fan:0.0.0
done

set -e

# docker logout $DOCKER_REGISTRY_ACCOUNT
