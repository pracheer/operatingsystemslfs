'''
Created on Dec 6, 2010

@author: Pracheer (pg298)
'''
import threading
from Shell import Shell

class Test(threading.Thread):
    def __init__(self):
        threading.Thread.__init__ ( self )
        self.shell = Shell()
        self.runcommand("mkfs -reuse")
            
    def runcommand(self, command):
        args = command.split(" ")
        func = getattr(self.shell, args[0])
        func(args)
    
    def run(self):
        self.runcommand("create a 20")
        self.runcommand("write a " + 'a'*20)
        self.runcommand("mkdir pg298")
        self.runcommand("cd pg298")
        self.runcommand("mkdir pg298_2")
        self.runcommand("cd pg298_2")
        self.runcommand("mkdir pg298_3")
        self.runcommand("cd pg298_3")
        self.runcommand("create pg298file 30")
        self.runcommand("write pg298file "+ 'pg298'*10)
        self.runcommand("sync")
        
class Test2(threading.Thread):
    def __init__(self):
        threading.Thread.__init__ ( self )
        self.shell = Shell()
        self.runcommand("mkfs -reuse")
        
    def runcommand(self, command):
        args = command.split(" ")
        func = getattr(self.shell, args[0])
        func(args)
    
    def run(self):
        self.runcommand("create b 20")
        self.runcommand("write b " + 'b'*20)
        self.runcommand("mkdir pracheer")
        self.runcommand("cd pracheer")
        self.runcommand("mkdir pracheer_2")
        self.runcommand("cd pracheer_2")
        self.runcommand("mkdir pracheer_3")
        self.runcommand("cd pracheer_3")
        self.runcommand("create pg298file 30")
        self.runcommand("write pg298file "+ 'pg298'*10)
        self.runcommand("sync")
            

test1 = Test()
test2 = Test2()

test1.start()
test2.start()
