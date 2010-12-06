from threading import Lock, Condition
import threading
import shutil

class BackUpThread (threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__ ( self )
        self.srcfile = "D:\study\operating system prac\CS4410\mp3\mp3\src\mail.txt"
        self.destfile = "D:\study\operating system prac\CS4410\mp3\mp3\src\\backup.txt"
        self.mutex = Lock()
        self.cv = Condition(self.mutex)
        self.msgCount = 0
        
    def run(self):
        with self.mutex:
            while True:
                # TODO: BUG here.
                while self.msgCount != 32:
                    self.cv.wait()

                print "Backing up the mail file."
#                TODO: copy only the new part.
#                desthandle = open(self.destfile, "r")
#                desthandle.seek(0, 2)
#                offset = desthandle.tell()
                shutil.copyfile(self.srcfile, self.destfile)
                self.msgCount = 0

    def newMsg(self):
        with self.mutex:
            self.msgCount += 1
            if self.msgCount == 32:
                self.cv.notifyAll()