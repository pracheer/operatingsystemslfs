#!/usr/bin/python
import sys, struct
import Segment
import InodeMap

from threading import Thread, Lock, Condition, Semaphore
from Segment import SegmentManagerClass
from Disk import DiskClass
from Inode import Inode, getmaxinode, setmaxinode
from InodeMap import InodeMapClass
from FileDescriptor import FileDescriptor
from DirectoryDescriptor import DirectoryDescriptor
from Constants import FILENAMELEN, DELETEDNODEID, PARENTDIR, CURRENTDIR
from FSE import FileSystemException
import Disk

def find_parent_name(path):
    parent, sep, element = path.rpartition("/")
    if parent == '':
        parent = '/'
    return parent

def find_filename(path):
    parent, sep, element = path.rpartition("/")
    return element

#takes an absolute path, iterates through the components in the name
def get_path_components(path):
    for component in path[1:].strip().split("/"):
        yield component

class LFSClass:
    def __init__(self, initdisk=True):
        pass

    # open an existing file or directory
    def open(self, path, isdir=False):
        inodenumber = self.searchfiledir(path)
        if (inodenumber is None) | (inodenumber is DELETEDNODEID):
            raise FileSystemException("Path Does Not Exist")
        # create and return a Descriptor of the right kind
        if isdir:
            return DirectoryDescriptor(inodenumber)
        else: 
            return FileDescriptor(inodenumber)
    
    def create(self, filename, isdir=False):
        fileinodenumber = self.searchfiledir(filename)
        if fileinodenumber is not None:
            raise FileSystemException("File Already Exists")

        # create an Inode for the file
        # Inode constructor writes the inode to disk and implicitly updates the inode map
        newinode = Inode(isdirectory=isdir)

        # now append the <filename, inode> entry to the parent directory
        parentdirname = find_parent_name(filename)
        parentdirinodenumber = self.searchfiledir(parentdirname)
        if parentdirinodenumber is None:
            raise FileSystemException("Parent Directory Does Not Exist")
        parentdirblockloc = InodeMap.inodemap.lookup(parentdirinodenumber)
        parentdirinode = Inode(str=Segment.segmentmanager.blockread(parentdirblockloc))
        self.append_directory_entry(parentdirinode, find_filename(filename), newinode)
        if isdir:
            self.append_directory_entry(newinode, CURRENTDIR, newinode)
            self.append_directory_entry(newinode, PARENTDIR, parentdirinode)
        
        if isdir:
            return DirectoryDescriptor(newinode.id)
        else:
            return FileDescriptor(newinode.id)

    # return metadata about the given file
    def stat(self, pathname):
        inodenumber = self.searchfiledir(pathname)
        # pracheer:
        if (inodenumber is None) | (inodenumber == DELETEDNODEID):
            raise FileSystemException("File or Directory Does Not Exist:"+pathname)
            
        inodeblocknumber = InodeMap.inodemap.lookup(inodenumber)
        inodeobject = Inode(str=Segment.segmentmanager.blockread(inodeblocknumber))
        return inodeobject.filesize, inodeobject.isDirectory

    # delete the given file
    def unlink(self, pathname):
        fileinode = self.searchfiledir(pathname)
        fileinodeblocknum = InodeMap.inodemap.lookup(fileinode)
        fileinodeobject = Inode(str=Segment.segmentmanager.blockread(fileinodeblocknum))
        if fileinodeobject.isDirectory :
            dd = DirectoryDescriptor(fileinodeobject.id)
            for name, inode in dd.enumerate():
                if (name != CURRENTDIR) & (name != PARENTDIR) & (inode != DELETEDNODEID):
                    raise FileSystemException("Directory not empty.")
            
        parent = find_parent_name(pathname)
        filename = find_filename(pathname)
        parentinode = self.searchfiledir(parent)
        parentinodeblocknum = InodeMap.inodemap.lookup(parentinode)
        parentinodeobject = Inode(str=Segment.segmentmanager.blockread(parentinodeblocknum))
        if parentinodeobject.isDirectory :
            dd = DirectoryDescriptor(parentinodeobject.id)
            charcount = 0;
            for name, inode in dd.enumerate():
                if name == filename :
                    parentinodeobject.write(charcount, struct.pack("%dsI" % FILENAMELEN, name, DELETEDNODEID), skip_inodemap_update = False)
                else :  
                    charcount += 32
        
    # write all in memory data structures to disk
    def sync(self):
        # pracheer:
        newinode = Inode(isdirectory=False)
        maxinode = getmaxinode()
        str, generationcount = InodeMap.inodemap.save_inode_map(maxinode)
        newinode.write(offset=0, data=str, skip_inodemap_update=True)
        blockno = Segment.segmentmanager.write_to_newblock(newinode.serialize())
        Segment.segmentmanager.update_inodemap_position(blockno, generationcount)
        Segment.segmentmanager.flush()

    # restore in memory data structures (e.g. inode map) from disk
    def restore(self):
        imlocation = Segment.segmentmanager.locate_latest_inodemap()
        iminode = Inode(str=Disk.disk.blockread(imlocation))
        imdata = iminode.read(0, 10000000)
        # restore the latest inodemap from wherever it may be on disk
        setmaxinode(InodeMap.inodemap.restore_inode_map(imdata))

    # given a parent's nodeid search for a particular child within its children
    # and return the nodeid of the child found.
    # pracheer:
    def search_inode_in_parent(self, childname, parentinodeid):
        if( (childname == None) | (childname == "") ):
            return parentinodeid
        
        inodeblocknumber = InodeMap.inodemap.lookup(parentinodeid)
        inodeobject = Inode(str=Segment.segmentmanager.blockread(inodeblocknumber))
        if(inodeobject.isDirectory):
            dd = DirectoryDescriptor(inodeobject.id)
            for name, inode in dd.enumerate():
                if (name == childname) & (inode != DELETEDNODEID): 
                    return inode
        return None
        
    # for a given file or directory named by path,
    # return its inode number if the file or directory exists,
    # else return None
    def searchfiledir(self, path):
        # pracheer:
        splits = path.split("/")
        parentinodeid = 1
        i = 1;
        while( (i < len(splits)) & ((parentinodeid!=None) | (parentinodeid!="") )):
            nodeid = self.search_inode_in_parent(splits[i], parentinodeid)
            i += 1
            parentinodeid = nodeid
            
        return nodeid

    # add the new directory entry to the data blocks,
    # write the modified inode to the disk,
    # and update the inode map
    def append_directory_entry(self, dirinode, filename, newinode):
        dirinode.write(dirinode.filesize, struct.pack("%dsI" % FILENAMELEN, filename, newinode.id))
    
            
filesystem = None        

