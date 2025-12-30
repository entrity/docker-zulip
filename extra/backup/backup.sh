set -eu

BASENAME="zulip-backup-$(date +%Y-%m-%d).tar.gz"
CONTAINER_FILE="/tmp/host-tmp/${BASENAME}"
LOCAL_FILE="/tmp/${BASENAME}"
CANONICAL_PATH="$HOME/zulip-backups/${BASENAME}"

debug() { >&2 echo -e "\x1b[33m$*\x1b[0m"; }

# Create backup file inside container but in a mounted directory so that it appears on host
cd /var/www/zulip/docker-zulip
docker compose exec -u zulip zulip /home/zulip/deployments/current/manage.py backup --output "$CONTAINER_FILE"
debug "Backup created in container at ${LOCAL_FILE}"

# Move backup file and symlink it
mkdir -p "$HOME/zulip-backups"
mv "$LOCAL_FILE" "${CANONICAL_PATH}"
debug "Moved backup to ${CANONICAL_PATH}"
for link_name in "${@}"; do
	ln -sf "${CANONICAL_PATH}" "$HOME/zulip-backups/${link_name}"
	debug "Symlinked to ${link_name}"
done

>&2 echo -e "\x1b[32;1mBackup process completed successfully.\x1b[0m"
