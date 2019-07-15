# Author:
#   Alan Tai
# Program:
#   Init MongoDB
# Date:
#   7/13/2019

set -e

# export variables
source /app/scripts/env_variables
# set default dir
CWD=$(pwd)

finish() {
  local existcode=$?
  cd $CWD
  exit $existcode
}

trap "finish" INT TERM

set +e

init_users_and_dbs() {
  # Create admin user
  echo "Creating users: \"$USER\"..."
  mongo $DB --eval "db.createUser({ user: '$MONGO_ADMIN_USER', pwd: '$MONGO_ADMIN_PASSWORD', roles: [ { role: 'userAdminAnyDatabase', db: 'admin' } ] });"
  mongo $DB --eval "db.createUser({ user: '$MONGO_TEST_USER', pwd: '$MONGO_TEST_PASSWORD', roles: [ { role: 'readWrite', db: '$MONGO_CONTROL_SYSTEM_DB' } ] });"
  mongo $DB --eval "db.createUser({ user: '$MONGO_TEST_USER', pwd: '$MONGO_TEST_PASSWORD', roles: [ { role: 'readWrite', db: '$MONGO_SUBSYSTEM_DB' } ] });"
  mongo $DB --eval "db.createUser({ user: '$MONGO_TEST_USER', pwd: '$MONGO_TEST_PASSWORD', roles: [ { role: 'readWrite', db: '$MONGO_FAN_DB' } ] });"

}

# Start MongoDB service
/usr/bin/mongod --dbpath /data --nojournal &
while ! nc -vz localhost $MONGO_PORT; do sleep 1; done

init_users_and_dbs

# Stop MongoDB service
/usr/bin/mongod --dbpath /data --shutdown

set -
