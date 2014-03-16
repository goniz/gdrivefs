#!/usr/bin/python2

from __future__ import with_statement

import os
import sys
import errno

from fuse import FUSE, FuseOSError, Operations

import gdrive


class GDriveFS(Operations):
	def __init__(self, root):
		self.root = root
		self.gdrive = gdrive.GDriveService()

	# Filesystem methods
	# ==================

	def access(self, path, mode):
		pass

	def chmod(self, path, mode):
		pass

	def chown(self, path, uid, gid):
		pass

	def getattr(self, path, fh=None):
		pass

	def readdir(self, path, fh):
		dirents = ['.', '..']
		for f in self.gdrive._tree.folders():
			dirents.append(f._name)
		for f in self.gdrive._tree.files():
			dirents.append(f._name)
		for r in dirents:
			yield r

	def readlink(self, path):
		pass

	def mknod(self, path, mode, dev):
		pass

	def rmdir(self, path):
		return True

	def mkdir(self, path, mode):
		return 0

	def statfs(self, path):
		pass

	def unlink(self, path):
		pass

	def symlink(self, target, name):
		pass

	def rename(self, old, new):
		pass

	def link(self, target, name):
		pass

	def utimens(self, path, times=None):
		pass

	# File methods
	# ============

	def open(self, path, flags):
		pass

	def create(self, path, mode, fi=None):
		pass

	def read(self, path, length, offset, fh):
		pass

	def write(self, path, buf, offset, fh):
		pass

	def truncate(self, path, length, fh=None):
		pass

	def flush(self, path, fh):
		pass

	def release(self, path, fh):
		pass

	def fsync(self, path, fdatasync, fh):
		pass

def main():
	image_file, mountpoint = sys.argv
	FUSE(GDriveFS(mountpoint), mountpoint, foreground=True)

if __name__ == '__main__':
	main()

