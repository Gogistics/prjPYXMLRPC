#!/usr/local/bin/bash
# Author:
#   Alan Tai
# Program:
#   Spin up the whole topology
# Date:
#   7/22/2019

set -e

finish() {
  local existcode=$?
  cd $CWD
  exit $existcode
}

trap "finish" INT TERM

set -e
config_networks=$PWD/infra/scripts/config_networks.sh
spin_up_dbs=$PWD/infra/scripts/spin_up_dbs.sh
spin_up_control_system=$PWD/infra/scripts/spin_up_control_system.sh
spin_up_subsystems=$PWD/infra/scripts/spin_up_subsystems.sh
spin_up_fans=$PWD/infra/scripts/spin_up_fans.sh

if [[ -f $config_networks &&
      -f $spin_up_dbs &&
      -f $spin_up_control_system &&
      -f $spin_up_subsystems &&
      -f $spin_up_fans ]]; then
  ./infra/scripts/config_networks.sh &&
  ./infra/scripts/spin_up_dbs.sh &&
  ./infra/scripts/spin_up_control_system.sh &&
  ./infra/scripts/spin_up_subsystems.sh &&
  ./infra/scripts/spin_up_fans.sh
else
  echo "Some files are missing..."
  exit 1
fi