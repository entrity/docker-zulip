#!/bin/bash

. secrets.sh

set -x

mysql -h "$RAILS_DB_HOST" -P "$RAILS_DB_PORT" -u "$RAILS_DB_USER" -p"$RAILS_DB_PASS" "$RAILS_DB_NAME"
