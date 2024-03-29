import sys, struct
import Segment

from threading import Thread, Lock, Condition, Semaphore
from Inode import Inode
import InodeMap
from FSE import FileSystemException

fd_lock = Lock()

class FileDescriptor(object):
    def __init__(self, inodenumber):
        global  fd_lock
        self.fd_lock = fd_lock
        with self.fd_lock:
            object.__init__(self)
            self.inodenumber = inodenumber
            self.position = 0
            self.isopen = True
    
    def close(self):
        with self.fd_lock:
            if not self.isopen:
                raise FileSystemException("The File is Already Closed!")
            self.isopen = False

    def _getinode(self):
        # pracheer:
        if not self.isopen:
            raise FileSystemException("The File is Closed!")
        
        # find the inode's position on disk
        inodeblocknumber = InodeMap.inodemap.lookup(self.inodenumber)
        # get the inode
        inodeobject = Inode(str=Segment.segmentmanager.blockread(inodeblocknumber))
        return inodeobject

    def getlength(self):
        # pracheer:
        if not self.isopen:
            raise FileSystemException("The File is Closed!")

        inodeobject = self._getinode()
        return inodeobject.filesize

    def read(self, readlength):
        with self.fd_lock:
            # pracheer:
            if not self.isopen:
                raise FileSystemException("The File is Closed!")
            
            inodeobject = self._getinode()
            data = inodeobject.read(self.position, readlength)
            self.position += len(data)
            return data

    def write(self, data, overwrite = False):
        with self.fd_lock:
        # pracheer:
            if not self.isopen:
                raise FileSystemException("The File is Closed!")
            
            inodeobject = self._getinode()
            if(overwrite):
                inodeobject.write(0, data, skip_inodemap_update=False)
            else:
                inodeobject.write(inodeobject.filesize, data, skip_inodemap_update=False)
                
            self.position += len(data)