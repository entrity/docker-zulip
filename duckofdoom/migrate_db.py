#!./venv/bin/python3
'''
Copy Psandbox posts from Rails pedestrian site to Zulip pedestrian site.

Usage:
. venv/bin/activate
./migrate_db.py <batch_size>
'''

import sys, os

# Add the current directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'py_utils_for_migration'))
import secrets # A local file
from rails_db_adapter import RailsPost, RailsDbAdapter
from zulip_db_adapter import ZulipPost, ZulipDbAdapter

rails_db = RailsDbAdapter(
	host=secrets.RAILS_DB_HOST,
	user=secrets.RAILS_DB_USER,
	password=secrets.RAILS_DB_PASS,
	db=secrets.RAILS_DB_NAME
)

zulip_db = ZulipDbAdapter(
	host=secrets.ZULIP_DB_HOST,
	user=secrets.ZULIP_DB_USER,
	password=secrets.ZULIP_DB_PASS,
	db=secrets.ZULIP_DB_NAME
)

def copy_a_batch_of_messages_from_rails_to_zulip(starting_rails_post_id=99999, message_batch_size=1):
	print("Fetching Rails posts with id <= %d" % (starting_rails_post_id,))
	rails_posts = rails_db.fetch_posts(from_id=starting_rails_post_id, limit=message_batch_size)
	for rails_post in rails_posts:
		print("Migrating Rails post id %d" % (rails_post.id,))
		zulip_db.migrate_rails_psandbox_post(rails_post)
		starting_rails_post_id = rails_post.id - 1

# Of the posts that have already been copied from Rails to Zulip, what's the min
# Rails record id? If none has been copied over, return 100_000, which exceeds
# the last record in rails (17472).
def infer_last_migrated_rails_post_id():
	zulip_db.cursor.execute("SELECT min(id) FROM zerver_message")
	min_zulip_id = zulip_db.cursor.fetchone()[0] or 0
	return 100_000 + (min_zulip_id | (1 << 17))

batch_size = int(sys.argv[1])
# Work backward from the latest post in the Rails db
cursor = infer_last_migrated_rails_post_id() - 1 # 100_000 if no records have been migrated over yet
copy_a_batch_of_messages_from_rails_to_zulip(starting_rails_post_id=cursor, message_batch_size=batch_size)
