#!/usr/bin/python2

import httplib2
import pprint
import re
import stat
import socket

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile

__timeout = 5
socket.setdefaulttimeout(__timeout)

class MIME(object):
	Folder = 'application/vnd.google-apps.folder'

class File(object):
	def __init__(self, service, gfile):
		super(File, self).__init__()
		self.service = service
		if isinstance(gfile, str):
			self.gfile = service.CreateFile({'id': gfile})
		elif isinstance(gfile, GoogleDriveFile):
			self.gfile = gfile
		else:
			raise ValueError('gfile should be an ID string or a GoogleDriveFile instance!')

	def name(self):
		return self.gfile[u'title']

	def id(self):
		return self.gfile[u'id']

	def stat(self):
		ret = {}
		try:
			if not hasattr(self, '_st_size'):
				self._st_size = int(self.service.CreateFile({'id': self.id()})['fileSize'])
		except KeyError:
			self._st_size = 0
		except:
			raise

		ret[u'st_mode'] = stat.S_IFREG | 0755
		ret[u'st_ino'] = 0
		ret[u'st_dev'] = 0
		ret[u'st_nlink'] = 2
		ret[u'st_uid'] = 0
		ret[u'st_gid'] = 0
		ret[u'st_size'] = self._st_size
		ret[u'st_atime'] = 0
		ret[u'st_mtime'] = 0
		ret[u'st_ctime'] = 0
		return ret

	def get(self):
		return self.gfile.GetContentString()

	def read(self, offset, length):
		url = self.gfile.get('downloadUrl')
		if not url or not hasattr(self.gfile.auth.service, '_http'):
			raise RuntimeError('no url, or no _http!')
		headers = { 'Range': 'bytes=%d-%d' % (offset, offset+length-1) }
		try:
			resp, content = self.gfile.auth.service._http.request(url, headers = headers)
			if resp.status != 206:
				raise RuntimeError('not 206 OK:', resp.status)
		except Exception as e:
			raise RuntimeError('Error while trying to download chunk')
		return content

	def __str__(self):
		return u'%s (f): %s' % (self.name(), self.id())

	@staticmethod
	def create_from_id(service, fid):
		gfile = service.CreateFile({'id': fid})
		return File(service, gfile)

class Folder(File):
	def __init__(self, service, gfile):
		super(Folder, self).__init__(service, gfile)
		query = "'%s' in parents and trashed=false" % (self.id(), )
		self._tree = self.service.ListFile({'q': query}).GetList()
		self.folders = list(self._folders())
		self.files = list(self._files())

	def _folders(self):
		for entry in self._tree:
			if entry[u'mimeType'] == MIME.Folder:
				yield Folder(self.service, entry)

	def _files(self):
		for entry in self._tree:
			if entry[u'mimeType'] != MIME.Folder:
				yield File(self.service, entry)

	def find_entry(self, name):
		f = filter(lambda x: x.name() == name, self.folders + self.files)
		if not f or len(f) > 1:
			return None
		return f[0]

	def stat(self):
		ret = super(Folder, self).stat()
		ret[u'st_mode'] = stat.S_IFDIR | 0755
		ret[u'st_size'] = 4096
		return ret

	def __str__(self):
		root = u'%s (d): %s' % (self.name(), self.id())
		for f in self.files:
			root += u'\n\t%s' % (unicode(f), )
		for f in self.folders:
			root += u'\n\t%s' % (unicode(f), )
		return root

	def __unicode__(self):
		return self.__str__()

class GDriveError(Exception):
	pass

class GDriveService(object):

	def __init__(self, config):
		print('Initializing GoogleDrive..')
		self._config = config
		self._authorize()
		self._service = GoogleDrive(self._gauth) 
		self._tree = Folder(self._service, 'root')
		print('Done')

	def _authorize(self):
		print('Authorizing..')
		self._gauth = GoogleAuth(self._config)
		self._gauth.LocalWebserverAuth()
		return self._gauth

	def resolve_path(self, path):
		print('Resolving', path, '...')
		if u'/' == path:
			print('found root!')
			return self._tree
		splitted = filter(None, path.split('/'))
		cur = self._tree
		for f in splitted:
			cur = cur.find_entry(f)
			if not cur:
				print('Not found??')
				return None
		print('Done!')
		return cur
