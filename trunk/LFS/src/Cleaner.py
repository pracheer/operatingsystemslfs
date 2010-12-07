'''
Created on Dec 7, 2010

@author: pracheer(pg298)
'''
import threading
from Constants import SEGMENTSIZE
from Segment import SuperBlock, segmentmanager
import Disk
from Inode import getmaxinode, Inode
import InodeMap
import struct
class Cleaner(threading.Thread):
    def __init__(self, startloc, endloc):
        threading.Thread.__init__ ( self )
        self.startloc = startloc
        self.endloc = endloc
        self.blockUseList = [False]*SEGMENTSIZE
        self.blockUseList[0] = True # super block is not free
        self.segNum = 0
        self.segBase = self.segNum * SEGMENTSIZE
        self.segSuperBlock=SuperBlock(data=Disk.disk.blockread(self.segBase))

    def markInodeData (self, inodeblocknumber):
        self.markUseBlock(inodeblocknumber)
        inodeobject = Inode(str=segmentmanager.blockread(inodeblocknumber))
        #mark the direct blocks
        for i in range(0, len(inodeobject.fileblocks)): 
            self.markUseBlock(inodeobject.fileblocks[i])
        #mark the indirect blocks
        if inodeobject.indirectblock != 0:
            indirectData = segmentmanager.blockread(inodeobject.indirectblock)
            for i in range (0, len(indirectData)/4):
                blockid = struct.unpack("I", indirectData[ i*4:(i*4 + 4) ] )[0]
                self.markUseBlock(blockid)
 
    def markUseBlock (self, blockno):
        if blockno >= self.segBase and blockno < (self.segBase + SEGMENTSIZE):
            self.blockUseList[blockno-self.segBase] = True
        
    def iterateInodeMap (self):
        for i in range (1, getmaxinode()):
            self.markInodeData(InodeMap.inodemap.lookup(i))
            
    def markSBdata(self):
        if self.segSuperBlock.inodemaplocation != 0:
            self.markInodeData(self.segSuperBlock.inodemaplocation)
            
    def markFreeSegmentBlocks (self, segno):
        self.blockUseList = [False]*SEGMENTSIZE
        self.blockUseList[0] = True
        self.segNum = segno
        self.segBase = self.segNum * SEGMENTSIZE
        self.segSuperBlock=SuperBlock(data=Disk.disk.blockread(self.segBase))
        self.markSBdata()
        self.iterateInodeMap()
        
        for i in range (1, SEGMENTSIZE):
            if (self.blockUseList == False):
                self.segSuperBlock.blockinuse[i] = self.blockUseList[i]
                
        Disk.disk.blockwrite(self.segBase, self.segSuperBlock.serialize())
     
    def run (self):
        if not (self.startloc >= 0 and self.endloc <= self.endloc and self.endloc <=SEGMENTSIZE):
            return
        segno = self.startloc
        while (segno < self.endloc):
            segno += segno + 1
            self.markFreeSegmentBlocks(segno)