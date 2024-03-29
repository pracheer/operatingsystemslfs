import pickle
import sys, struct, os, random, math, pickle
from threading import Thread, Lock, Condition, Semaphore

from Disk import *
from Constants import FILENAMELEN, DELETEDNODEID
from FileDescriptor import FileDescriptor
from FSE import FileSystemException

lock = Lock()

class DirectoryDescriptor(FileDescriptor):
    def __init__(self, inodenumber):
        global lock
        with lock:
            super(DirectoryDescriptor, self).__init__(inodenumber)
            inodeobject = self._getinode()
            if not inodeobject.isDirectory:
                raise FileSystemException("Not a directory - inode %d" % inodenumber)

    def enumerate(self):
        length = self.getlength()
        numentries = length / (FILENAMELEN + 4)  # a directory entry is a filename and an integer for the inode number
        # pracheer:
        data = self.read(length)
        for i in range(0, numentries):
            start = i*(FILENAMELEN + 4)
            name, inode = struct.unpack("%dsI" % (FILENAMELEN,), data[start:start+(FILENAMELEN+4)])
            name = name.strip('\x00')
            yield name, inode
