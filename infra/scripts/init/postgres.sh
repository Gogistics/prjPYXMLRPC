# Author:
#   Alan Tai
# Program:
#   Init postgres
# Date:
#   7/13/2019

set -e

# set default dir
CWD=$(pwd)

finish() {
  local existcode=$?
  cd $CWD
  exit $existcode
}

trap "finish" INT TERM


set +e
# env variables
POSTGRES_ADMIN_USER="postgres"
POSTGRES_TEST_USER="isi_test_user"
POSTGRES_TEST_USER_PASSWORD="isi_test_user_123"
POSTGRES_CONTROL_SYSTEM_DB="control_system"

init_users_and_dbs() {
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_ADMIN_USER" <<-EOSQL
    CREATE USER $POSTGRES_TEST_USER WITH PASSWORD '$POSTGRES_TEST_USER_PASSWORD';
    CREATE DATABASE $POSTGRES_CONTROL_SYSTEM_DB;

    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_CONTROL_SYSTEM_DB TO $POSTGRES_TEST_USER;

    \c $POSTGRES_CONTROL_SYSTEM_DB;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $POSTGRES_TEST_USER;
    CREATE TABLE configuration_subsystem(
      id SERIAL PRIMARY KEY,
      comp_id VARCHAR(20) NOT NULL UNIQUE,
      ip INET NOT NULL UNIQUE,
      port INT NOT NULL,
      tstz TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE configuration_fan(
      id SERIAL PRIMARY KEY,
      comp_id VARCHAR(20) NOT NULL UNIQUE,
      ip INET NOT NULL UNIQUE,
      port INT NOT NULL,
      tstz TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
EOSQL
}

init_users_and_dbs
set -e
