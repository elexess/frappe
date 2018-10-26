import os
import frappe


class DbManager:

	def __init__(self, db):
		"""
		Pass root_conn here for access to all databases.
		"""
		if db:
			self.db = db

	def get_current_host(self):
		return self.db.sql("select user()")[0][0].split('@')[1]

	def create_user(self, user, password, host=None):
		# Create user if it doesn't exist.
		if not host:
			host = self.get_current_host()

		if password:
			self.db.sql("CREATE USER '%s'@'%s' IDENTIFIED BY '%s';" % (user, host, password))
		else:
			self.db.sql("CREATE USER '%s'@'%s';" % (user, host))

	def delete_user(self, target, host=None):
		if not host:
			host = self.get_current_host()
		try:
			self.db.sql("DROP USER '%s'@'%s';" % (target, host))
		except Exception as e:
			if e.args[0] == 1396:
				pass
			else:
				raise

	def create_database(self, target):
		if target in self.get_database_list():
			self.drop_database(target)

		self.db.sql("CREATE DATABASE `%s` ;" % target)

	def drop_database(self, target):
		self.db.sql("DROP DATABASE IF EXISTS `%s`;" % target)

	def grant_all_privileges(self, target, user, host=None):
		if not host:
			host = self.get_current_host()

		self.db.sql("GRANT ALL PRIVILEGES ON `%s`.* TO '%s'@'%s';" % (target, user, host))

	def flush_privileges(self):
		self.db.sql("FLUSH PRIVILEGES")

	def get_database_list(self):
		"""get list of databases"""
		return [d[0] for d in self.db.sql("SHOW DATABASES")]

	@staticmethod
	def restore_database(target, source, user, password):
		from frappe.utils import make_esc
		esc = make_esc('$ ')

		from distutils.spawn import find_executable
		pipe = find_executable('pv')
		if pipe:
			pipe = '{pipe} {source} |'.format(
				pipe=pipe,
				source=source
			)
			source = ''
		else:
			pipe = ''
			source = '< {source}'.format(source=source)

		if pipe:
			print('Creating Database...')

		command = '{pipe} mysql -u {user} -p{password} -h{host} {target} {source}'.format(
			pipe=pipe,
			user=esc(user),
			password=esc(password),
			host=esc(frappe.db.host),
			target=esc(target),
			source=source
		)
		os.system(command)
