#!./venv/bin/python3

'''
I copied over all the sandbox posts, but I don't have channels and topics
assigned. So now I have to correlate that.

Usage:
./setup # If first time
. venv/bin/activate
./$0 <batch_size>
'''

import sys, os

# Add the current directory to sys.path
sys.path.append(os.getcwd())
import py_utils_for_migration.data_maps as data_maps
import py_utils_for_migration.secrets as secrets
from py_utils_for_migration.rails_db_adapter import RailsDbAdapter
from py_utils_for_migration.zulip_db_adapter import ZulipDbAdapter

class MapRailsVolumeToZulipSink(object):
	def __init__(self, rails_db, zulip_db):
		self.rails_db = rails_db
		self.zulip_db = zulip_db
		self._zulip_channels = None
		self._channel_map = None
		self._rails_volumes_by_ids = None

	def get(self, rails_volume_id):
		rails_volume = self._get_rails_volumes_by_ids()[str(rails_volume_id)]
		zulip_sink = self._get_channel_map()[rails_volume]
		return (zulip_sink, rails_volume)

	def upsert_topics(self):
		for rails, zulip in self._get_channel_map().items():
			print(f"{rails.p_title}|{zulip.stream_name}\t{rails.title}\t{zulip.stream_id} : {zulip.recipient_id}")
			self.zulip_db.upsert_topic(
				stream_id=zulip.stream_id,
				recipient_id=zulip.recipient_id,
				topic=rails.title,
			)

	def _get_rails_volumes_by_ids(self):
		if self._rails_volumes_by_ids: return self._rails_volumes_by_ids

		self._rails_volumes_by_ids = { rv.id: rv for rv in data_maps.RAILS_VOLUMES }
		return self._rails_volumes_by_ids

	def _get_zulip_channels(self):
		if self._zulip_channels: return self._zulip_channels

		self._zulip_channels = self.zulip_db.get_sinks()
		return self._zulip_channels

	def _get_channel_map(self):
		if self._channel_map: return self._channel_map

		zulip_sinks = self._get_zulip_channels()
		callback = lambda rails_volume: self._create_zulip_sink(rails_volume)
		self._channel_map = data_maps.ChannelMapBuilder(zulip_sinks).get_map()
		return self._channel_map

	def _create_zulip_sink(self, rails_volume):
		print("Creating new sink for ", rails_volume, file=sys.stderr)

class PostsUpdater(object):
	def __init__(self, rails_db, zulip_db):
		self.rails_db = rails_db
		self.zulip_db = zulip_db
		self.mapper = MapRailsVolumeToZulipSink(rails_db, zulip_db)

	def call(self):
		self._update_posts()
		self.mapper.upsert_topics()

	def _update_post(self, rails_post):
		zulip_sink, rails_volume = self.mapper.get(rails_post.volume_id)
		# print('post id', rails_post.id, 'topic', zulip_sink.recipient_id, rails_volume.title[0:60])
		self.zulip_db.cursor.execute("""
			UPDATE zerver_message
			SET recipient_id = %s, subject = %s
			WHERE id = %s AND content = %s
		""", (zulip_sink.recipient_id, rails_volume.title[0:60], rails_post.id, rails_post.content))
		n_rows = self.zulip_db.cursor.rowcount
		assert n_rows == 1
		self.zulip_db.conn.commit()

	def _update_posts(self):
		rails_posts = self.rails_db.fetch_posts(from_id=0, limit=99999, where=["volume_id != 1"])
		print(f"n rails_posts: {len(rails_posts)}")
		for rails_post in rails_posts:
			try:
				self._update_post(rails_post)
			except KeyError:
				print(f"\x1b[31mKeyError: rails volume id:\x1b[0m {rails_post.volume_id}")

if __name__ == '__main__':
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
	PostsUpdater(rails_db, zulip_db).call()
