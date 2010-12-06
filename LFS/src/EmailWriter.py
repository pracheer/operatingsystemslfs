from threading import Lock, Condition, Semaphore
from Shell import Shell
import time

class EmailWriter:
    
    def __init__(self):
        self.shell = Shell()
        self.runcommand("mkfs -reuse")
        self.msgcount = 0
        self.mutex = Lock()
        
    def write(self, msg, mailto):
        with self.mutex:
            print "writing emails to LFS"
            mailto = mailto.strip()
            filename = time.clock()
            self.runcommand("cd /mails/"+mailto)
            self.runcommand("create " + str(filename) + " 20")
            self.runcommand("write " + str(filename) + " " + msg)
            self.msgcount += 1
            self.runcommand("sync")
            print "Writing to LFS completed."
            
    def runcommand(self, command):
        args = command.split(" ")
        func = getattr(self.shell, args[0])
        func(args)
                