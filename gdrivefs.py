#!/usr/bin/python2

import os
import sys
import errno
import fuse
import gdrive

CONFIG_DIR = '%s/.gdrivefs' % (os.getenv('HOME'), )
CONFIG_PATH = '%s/settings.yaml' % (CONFIG_DIR, )

class GDriveFS(fuse.Operations):
	def __init__(self, root, config):
		self.root = root
		self.config = config
		self.gdrive = gdrive.GDriveService(config)

	# Filesystem methods
	# ==================

	def access(self, path, mode):
		print('access')
		return 0

	def chmod(self, path, mode):
		print('chmod')
		pass

	def chown(self, path, uid, gid):
		print('chown')
		pass

	def getattr(self, path, fh=None):
		print('getattr')
		root = self.gdrive.resolve_path(path)
		return root.stat()

	def readdir(self, path, fh):
		print('readdir')
		dirents = ['.', '..']
		root = self.gdrive.resolve_path(path)
		for f in root.folders:
			dirents.append(f.name())
		for f in root.files:
			dirents.append(f.name())
		for r in dirents:
			yield r

	def readlink(self, path):
		print('readlink')
		pass

	def mknod(self, path, mode, dev):
		print('mknod')
		pass

	def rmdir(self, path):
		print('rmdir')
		return True

	def mkdir(self, path, mode):
		print('mkdir')
		return 0

	def statfs(self, path):
		print('statfs')
		pass

	def unlink(self, path):
		print('unlink')
		pass

	def symlink(self, target, name):
		print('symlink')
		pass

	def rename(self, old, new):
		print('rename')
		pass

	def link(self, target, name):
		print('link')
		pass

	def utimens(self, path, times=None):
		print('utimens')
		pass

	# File methods
	# ============

	def open(self, path, flags):
		print('open')
		return 0

	def create(self, path, mode, fi=None):
		print('create')
		pass

	def read(self, path, length, offset, fh):
		print('read')
		root = self.gdrive.resolve_path(path)
		return root.read(offset, length)

	def write(self, path, buf, offset, fh):
		print('write')
		pass

	def truncate(self, path, length, fh=None):
		print('truncate')
		pass

	def flush(self, path, fh):
		print('flush')
		pass

	def release(self, path, fh):
		print('release')
		pass

	def fsync(self, path, fdatasync, fh):
		print('fsync')
		pass

def main():
	image_file, mountpoint = sys.argv
	fuse.FUSE(GDriveFS(mountpoint, CONFIG_PATH), mountpoint, foreground=True)
	return 0

if __name__ == '__main__':
	ret = main()
	sys.exit(ret)

