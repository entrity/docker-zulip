#!./venv/bin/python3
'''
Copy Psandbox posts from Rails pedestrian site to Zulip pedestrian site.

Usage:
. venv/bin/activate
./migrate_db.py <batch_size>
'''

import sys, os
import MySQLdb
import psycopg2
import psycopg2.extras
from collections import namedtuple

# Add the current directory to sys.path
sys.path.append(os.getcwd())
import secrets # A local file

# ZULIP_PSANDBOX_RECIPIENT_ID = 11 # stream 2: sandbox, not Psandbox
ZULIP_PSANDBOX_RECIPIENT_ID = 10 # stream 3: Psandbox

# Data model for a post in the Rails db
RailsPost = namedtuple('RailsPost', ['id', 'idx', 'volume_id', 'user_id', 'content', 'created_at', 'updated_at', 'timestamp', 'user_name'])

# Data model for a post in the Zulip db
ZulipPost = namedtuple('ZulipPost', ['id', 'type', 'subject', 'content', 'rendered_content', 'rendered_content_version', 'date_sent', 'last_edit_time', 'edit_history', 'has_attachment', 'has_image', 'has_link', 'search_tsvector', 'sender_id', 'sending_client_id', 'realm_id', 'recipient_id', 'is_channel_message'])

class RailsDbAdapter(object):
	def __init__(self, host, user, password, db):
		self.conn = MySQLdb.connect(host=host, user=user, passwd=password, db=db)
		self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

	def fetch_post_rows(self, from_id=0, limit=10):
		self.cursor.execute("SELECT * FROM posts where id <= %d order by id desc limit %d" % (from_id, limit))
		return self.cursor.fetchall()

	def fetch_posts(self, from_id=0, limit=10):
		rows = self.fetch_post_rows(from_id=from_id, limit=limit)
		return [self.obj_for_row(row) for row in rows]

	def close(self):
		self.cursor.close()
		self.conn.close()

	def obj_for_row(self, row):
		args = [row[k] for k in RailsPost._fields]
		return RailsPost(*args)

class ZulipDbAdapter(object):
	def __init__(self, host, user, password, db):
		self.conn = psycopg2.connect(host=host, user=user, password=password, dbname=db)
		self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

	def fetch_posts(self, from_id=0, limit=10):
		self.cursor.execute("SELECT * FROM zerver_message order by id desc limit 1")
		return self.cursor.fetchall()

	def insert_post(self, post):
		self.cursor.execute("""
			INSERT INTO zerver_message (
				realm_id, type, id, sender_id, sending_client_id, is_channel_message,
				recipient_id, content, rendered_content, date_sent,
				subject, has_attachment, has_image, has_link, rendered_content_version
			)
			VALUES (
				2, 1, %s, %s, %s, 't',
				%s, %s, %s, %s,
				%s, 'f', 'f', 'f', 1
			)
			""",
			(
				post['id'], post['sender_id'], post['sending_client_id'],
				post['recipient_id'], post['content'], post['rendered_content'], post['date_sent'],
				post['subject']
			)
		)
		self.conn.commit()

	def close(self):
		self.cursor.close()
		self.conn.close()

	def migrate_rails_psandbox_post(self, rails_post):
		sender_id = map_rails_user_id_to_zulip_user_id(rails_post.user_id)
		if sender_id is None:
			print("Skipping post id %d: no mapping for Rails user id %d" % (rails_post.id, rails_post.user_id))
			return

		zulip_post = {
			'id': (rails_post.id - 100_000) & ~(1 << 17), # negative to put it earlier than existing posts
			'subject': '',
			'sender_id': sender_id,
			'sending_client_id': 10, # Data migration from Rails
			'recipient_id': ZULIP_PSANDBOX_RECIPIENT_ID,
			'content': rails_post.content,
			'rendered_content': rails_post.content,
			'date_sent': rails_post.created_at
		}
		self.insert_post(zulip_post)

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

def map_rails_user_id_to_zulip_user_id(rails_user_id):
	return {
		1:9, 2:9, 3:9, 4:9, # | otto (auto-bot), created by me
		5:  8,  # | m.a
		6: 14, # | r.al
		8: 19, # | m.chr
		9:  11, # | j.cl
		12: 12, # | m.cr
		14: 16, # | t.ro
		15: 10, # | l.ty
		16: 21, # n.to
		13: 20, # | c.pf
		7: 17, # | r.wi
		18: 15, # | d.th
		19: 18, # | j.lo
	}.get(rails_user_id, None)

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
