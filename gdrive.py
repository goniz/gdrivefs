#!/usr/bin/python2

import httplib2
import pprint

import apiclient.discovery
from apiclient import errors
from oauth2client.client import OAuth2WebServerFlow

class File(object):
	def __init__(self, name, fid):
		self._name = name
		self._id = fid
		self._metadata = None

	def set_metadata(self, meta):
		self._metadata = meta

	def __str__(self):
		return u'%s (f): %s' % (self._name, self._id)

class Folder(object):
	def __init__(self, name, fid):
		self._name = name
		self._id = fid
		self._folders = []
		self._files = []
		self._metadata = None

	def set_metadata(self, meta):
		self._metadata = meta

	def add_folder(self, folder):
		f = Folder(folder[u'title'], folder[u'id'])
		f.set_metadata(folder)
		self._folders.append(f)
		return f

	def add_folders(self, folders):
		for folder in folders:
			self.add_folder(folder)

	def add_file(self, f):
		tmpfile = File(f[u'title'], f[u'id'])
		tmpfile.set_metadata(f)
		self._files.append(tmpfile)
		return tmpfile

	def add_files(self, files):
		for f in files:
			self.add_file(f)

	def folders(self):
		return self._folders

	def files(self):
		return self._files

	def __str__(self):
		root = u'%s (d): %s' % (self._name, self._id)
		for f in self._files:
			root += u'\n\t%s' % (unicode(f), )
		for f in self._folders:
			root += u'\n\t%s' % (unicode(f), )
		return root

	def __unicode__(self):
		return self.__str__()

class GDriveError(Exception):
	pass

class GDriveService(object):
	# Check https://developers.google.com/drive/scopes for all available scopes
	OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

	# Redirect URI for installed apps
	REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

	def __init__(self, cid, csecret):
		self._client_id = cid
		self._client_secret = csecret
		self._authorize()
		self._entires = self._get_entries()
		self._tree = self._build_tree()

	def _authorize(self):
		# Run through the OAuth flow and retrieve credentials
		args =(self._client_id, self._client_secret, GDriveService.OAUTH_SCOPE, GDriveService.REDIRECT_URI)
		flow = OAuth2WebServerFlow(*args)
		authorize_url = flow.step1_get_authorize_url()
		print 'Go to the following link in your browser: ' + authorize_url
		code = raw_input('Enter verification code: ').strip()
		credentials = flow.step2_exchange(code)

		# Create an httplib2.Http object and authorize it with our credentials
		http = httplib2.Http()
		self._http = credentials.authorize(http)
		self._service = apiclient.discovery.build('drive', 'v2', http=self._http)
		return self._service

	def _get_entries(self):
		print 'Downloading entries...',
		result = []
		page_token = None
		while True:
			try:
				param = {}
				if page_token:
					param['pageToken'] = page_token
				files =  self._service.files().list(**param).execute()
				result.extend(files['items'])
				page_token = files.get('nextPageToken')
				if not page_token:
					break
			except errors.HttpError as error:
				print 'shit', str(error)
				break
		ret = filter(lambda x: x['userPermission']['id'] == 'me' and x['userPermission']['role'] == 'owner', result)
		print 'Done!'
		return ret

	def _find_root(self):
		entries = filter(lambda x: x['parents'] and x['parents'][0]['isRoot'], self._entires)
		if not entries:
			raise GDriveError('no root!?')
		tmpid = entries[0]['parents'][0]['id']
		tmplst = filter(lambda x: x['parents'][0]['id'] == tmpid, entries)
		assert len(tmplst) == len(entries), 'wtf? should be only one root!'
		return tmpid

	def _find_children(self, fid):
		root = filter(lambda x: x['parents'] and x['parents'][0]['id'] == fid, self._entires)
		folders = filter(lambda x: x['mimeType'] == 'application/vnd.google-apps.folder', root)
		files = filter(lambda x: x['mimeType'] != 'application/vnd.google-apps.folder', root)
		return (files, folders)

	def _populate_folder(self, folder):
		myid = folder._id
		files, folders = self._find_children(myid)
		if files:
			# add files dicts to current folder obj
			folder.add_files(files)
		if folders:
			# add folders dicts to current folder obj
			folder.add_folders(folders)
			# populate each new folder with its childern
			for folder in folder.folders():
				self._populate_folder(folder)

	def _build_tree(self):
		print 'Building Filesystem Tree..',
		root_id = self._find_root()
		root = Folder('/', root_id)
		self._populate_folder(root)
		print 'Done!'
		return root
