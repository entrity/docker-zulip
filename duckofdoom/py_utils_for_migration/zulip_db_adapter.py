import psycopg2
import psycopg2.extras
from collections import namedtuple
import sys

from .data_maps import map_rails_user_id_to_zulip_user_id
# from .data_maps import map_rails_volume_name_to_zulip_stream_id
from .rails_db_adapter import RailsPost

# ZULIP_PSANDBOX_RECIPIENT_ID = 11 # stream 2: sandbox, not Psandbox
ZULIP_PSANDBOX_RECIPIENT_ID = 10 # stream 3: Psandbox

DATA_IS_MIGRATED_FROM_RAILS_CLIENT_ID = 10 # I created this client manually in the db

MARKHAM_USER_ID = 10 # My user id in the Zulip Pedestrian realm
PEDESTRIAN_REALM_ID = 2

# Data model for a post in the Zulip db
ZulipPost = namedtuple('ZulipPost', ['id', 'type', 'subject', 'content', 'rendered_content', 'rendered_content_version', 'date_sent', 'last_edit_time', 'edit_history', 'has_attachment', 'has_image', 'has_link', 'search_tsvector', 'sender_id', 'sending_client_id', 'realm_id', 'recipient_id', 'is_channel_message'])
ZulipRecipient = namedtuple('ZulipRecipient', ['stream_id', 'recipient_id', 'stream_name'])

def build_zulip_post_from_rails_post(rails_post: RailsPost) -> ZulipPost:
	sender_id = map_rails_user_id_to_zulip_user_id(rails_post.user_id)
	return ZulipPost(
		id=None,
		type=1,
		subject='', # todo: story_name
		content=rails_post.content,
		rendered_content=rails_post.content,
		rendered_content_version=1,
		date_sent=rails_post.created_at,
		last_edit_time=None,
		edit_history=None,
		has_attachment=False,
		has_image=False,
		has_link=False,
		search_tsvector=None,
		sender_id=sender_id,
		sending_client_id=DATA_IS_MIGRATED_FROM_RAILS_CLIENT_ID,
		realm_id=2, # the "psandbox" realm
		recipient_id=recipient_id,
		is_channel_message=True,
	)

class ZulipDbAdapter(object):
	def __init__(self, host, user, password, db):
		print('connecting to postgresql db...', db, file=sys.stderr)
		self.conn = psycopg2.connect(host=host, user=user, password=password, dbname=db)
		self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

	def fetch_posts(self, from_id=0, limit=10):
		self.cursor.execute("SELECT * FROM zerver_message order by id desc limit 1")
		return self.cursor.fetchall()

	def insert_post(self, post: ZulipPost):
		items = { k:v for k,v in post._asdict().items() if v is not None }
		values_placeholders = ','.join(['%s' for k in items.keys()])
		columns = ','.join(items.keys())
		self.cursor.execute(f"""
			INSERT INTO zerver_message ({columns})
			VALUES ({values_placeholders})
			RETURNING id""",
			tuple(items.values())
		)
		self.conn.commit()

	def upsert_topic(self, topic: str, recipient_id: str|int, stream_id: str|int) -> None:
		self.cursor.execute("""
		INSERT INTO zerver_usertopic
		(topic_name, recipient_id, stream_id, user_profile_id, last_updated, visibility_policy)
		VALUES (%s, %s, %s, %s, now(), 3)
		ON CONFLICT DO NOTHING
		""", (topic, recipient_id, stream_id, MARKHAM_USER_ID))

	def get_sinks(self):
		self.cursor.execute("""
		SELECT r.id AS recipient_id, s.id AS stream_id, name FROM zerver_recipient r
		JOIN zerver_stream s ON s.recipient_id = r.id
		WHERE realm_id = %s
		ORDER BY name
		""", (PEDESTRIAN_REALM_ID,))
		return [build_zulip_recipient_from_db(row) for row in self.cursor.fetchall()]

	def insert_topic(self, sink):
		# select r.*, s.* from zerver_recipient r join zerver_stream s on s.recipient_id = r.id order by name;
		# insert into zerver_usertopic
		# (topic_name,visibility_policy,recipient_id,stream_id,user_profile_id,last_updated)
		# values ('Reshaped and Returned part 3',3,52,26,10,now());
		columns = "topic_name, visibility_policy, recipient_id, stream_id, user_profile_id, last_updated"
		placeholders = "%s, %s, %s, %s, %s, %s"
		values = (sink.topic, 3, sink.recipient_id, sink.stream_id, MARKHAM_USER_ID, 'now()')
		self.cursor.execute(f"INSERT INTO zerver_usertopic ({columns}) values ({placeholders}) RETURNING id;", values)
		self.conn.commit()

	def close(self):
		self.cursor.close()
		self.conn.close()

	def migrate_rails_psandbox_post(self, rails_post: RailsPost):
		zulip_post = build_zulip_post_from_rails_post(rails_post)
		zulip_post.recipient_id = ZULIP_PSANDBOX_RECIPIENT_ID
		zulip_post.subject = ''
		zulip_post.id = rails_post.id
		self.insert_post(zulip_post)

	# def migrate_rails_post(self, rails_post: RailsPost, volume_name: str, story_name: str):
	# 	zulip_post = build_zulip_post_from_rails_post(rails_post)
	# 	zulip_post.recipient_id = map_rails_volume_name_to_zulip_stream_id(volume_name)
	# 	zulip_post.subject = story_name
	# 	self.insert_post(zulip_post)

def build_zulip_recipient_from_db(row):
	return ZulipRecipient(row['stream_id'], row['recipient_id'], row['name'])
