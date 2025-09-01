#!/bin/bash

. secrets.sh

set -euo pipefail

export PGPASSWORD="$ZULIP_DB_PASS"

SQL_DUMP_FILE="$ZULIP_DB_NAME-$(date +%Y-%m-%d)".sql
pg_dump --host "$ZULIP_DB_HOST" --username "$ZULIP_DB_USER" --dbname "$ZULIP_DB_NAME" --file "$SQL_DUMP_FILE.tmp"
mv --debug --backup=numbered "$SQL_DUMP_FILE.tmp" "$SQL_DUMP_FILE"
