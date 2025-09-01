#!/bin/bash

. secrets.sh

set -x

export PGPASSWORD="$ZULIP_DB_PASS"

psql -h "$ZULIP_DB_HOST" -U "$ZULIP_DB_USER" -d "$ZULIP_DB_NAME" "${@}"
