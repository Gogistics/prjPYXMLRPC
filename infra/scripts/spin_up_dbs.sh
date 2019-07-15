#!/usr/local/bin/bash
# Author:
#   Alan Tai
# Program:
#   Spin up all databases
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
docker login -u $DOCKER_REGISTRY_USER_NAME -p $DOCKER_REGISTRY_PWD $DOCKER_REGISTRY_ACCOUNT

set +e
# build Docker images and
# Note: push the image to docker registry if needed

# Mongo
docker build -t alantai/isi_robot_system_mongo:0.0.0 \
  -f ./infra/Dockerfiles/Dockerfile.mongo .

# spin up container
docker run -d --name isi_robot_system_mongo \
  --network $DOCKER_NETWORK_ROBOT_SYSTEM \
  --ip $MONGO_IP \
  -e EXPOSE_PORT=$MONGO_PORT \
  --log-opt mode=non-blocking \
  --log-opt max-buffer-size=4m \
  --log-opt max-size=100m \
  --log-opt max-file=5 \
  alantai/isi_robot_system_mongo:0.0.0
# \Mongo

# Postgres
docker build -t alantai/isi_robot_system_postgres:0.0.0 \
  -f ./infra/Dockerfiles/Dockerfile.postgres .

# spin up container
docker run -d --name isi_robot_system_postgres \
  --network $DOCKER_NETWORK_ROBOT_SYSTEM \
  --ip $POSTGRES_IP \
  -e EXPOSE_PORT=$POSTGRES_PORT \
  --log-opt mode=non-blocking \
  --log-opt max-buffer-size=4m \
  --log-opt max-size=100m \
  --log-opt max-file=5 \
  alantai/isi_robot_system_postgres:0.0.0
# \Postgres

# Redis
docker build -t alantai/isi_robot_system_redis:0.0.0 \
  -f ./infra/Dockerfiles/Dockerfile.redis .

# spin up container
docker run -d --name isi_robot_system_redis \
  --network $DOCKER_NETWORK_ROBOT_SYSTEM \
  --ip $REDIS_IP \
  -e EXPOSE_PORT=$REDIS_PORT \
  --log-opt mode=non-blocking \
  --log-opt max-buffer-size=4m \
  --log-opt max-size=100m \
  --log-opt max-file=5 \
  alantai/isi_robot_system_redis:0.0.0
# \Redis

set -e

docker logout $DOCKER_REGISTRY_ACCOUNT
