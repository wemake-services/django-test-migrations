#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

_SETUP_SCRIPT="$(cat << EOM
  CREATE DATABASE IF NOT EXISTS db;
  GRANT ALL PRIVILEGES ON db.* TO django;
  FLUSH PRIVILEGES;
EOM
)"
mysql \
  --host="${DJANGO_DATABASE_HOST}" \
  --port="${DJANGO_DATABASE_PORT}" \
  --user="root" \
  --password="superpasswd123" \
  --execute="${_SETUP_SCRIPT}"
