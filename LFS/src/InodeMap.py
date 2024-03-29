import struct
import Segment
from Segment import SegmentClass
from Constants import DELETEDNODEID
from threading import Lock

lock = Lock()

# the task of the InodeMap is to map inodes to their
# position on the disk
class InodeMapClass:
    def __init__(self):
        self.lock = lock
        with self.lock:
            self.mapping = {}
            self.generationcount=1

    # given an abstract inode identifier, returns the
    # on-disk block address for the inode
    def lookup(self, inodeno):
        with self.lock:
            if not self.mapping.has_key(inodeno):
                print "Lookup for inode failed because that inode was never created", inodeno
    
            return self.mapping[inodeno]

    # following the write of an inode, update the
    # inode map with the new position of the inode
    # on the disk
    def update_inode(self, inodeid, inodedata):
        with self.lock:
            inodeblockloc = Segment.segmentmanager.write_to_newblock(inodedata)
            self.mapping[inodeid] = inodeblockloc

    # write the inodemap to the end of the current segment
    # 
    # the inode map is written to an invisible file, whose
    # inode in turn is stored in the superblock of the
    # segment
    def save_inode_map(self, iip):
        with self.lock:
            self.generationcount += 1
            str = struct.pack("I", iip) # Save maximum inodenumber
            for (key, val) in self.mapping.items():
                str += struct.pack("II", key, val)
            return str, self.generationcount

    # go through all segments, find the 
    # most recent segment, and read the latest valid inodemap
    # from the segment
    def restore_inode_map(self, imdata):
        with self.lock:
            self.mapping = {}
            iip = struct.unpack("I", imdata[0:4])[0]
            imdata = imdata[4:]
            for keyvaloffset in range(0, len(imdata), 8):
                key, val = struct.unpack("II", imdata[keyvaloffset:keyvaloffset+8])
                self.mapping[key] = val
            return iip

inodemap = None
