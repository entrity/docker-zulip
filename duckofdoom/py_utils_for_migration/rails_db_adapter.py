import MySQLdb
from collections import namedtuple
import sys

# Data model for a post in the Rails db
RailsPost = namedtuple('RailsPost', ['id', 'idx', 'volume_id', 'user_id', 'content', 'created_at', 'updated_at', 'timestamp', 'user_name'])

class RailsDbAdapter(object):
	def __init__(self, host, user, password, db):
		print('connecting to mysql db...', db, file=sys.stderr)
		self.conn = MySQLdb.connect(host=host, user=user, passwd=password, db=db)
		self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

	def fetch_post_rows(self, from_id=0, limit=10, where=[]):
		where_text = RailsDbAdapter.build_where_text(['id > %d', *where])
		query = f"SELECT * FROM posts {where_text} order by id desc limit %d" % (from_id, limit)
		self.cursor.execute(query)
		return self.cursor.fetchall()

	def fetch_posts(self, from_id=0, limit=10, where=[]):
		rows = self.fetch_post_rows(from_id=from_id, limit=limit, where=where)
		return [self.obj_for_row(row) for row in rows]

	def close(self):
		self.cursor.close()
		self.conn.close()

	def obj_for_row(self, row):
		args = [row[k] for k in RailsPost._fields]
		return RailsPost(*args)

	@staticmethod
	def build_where_text(where):
		return '' if len(where) == 0 else f"WHERE {" AND ".join(where)}"
