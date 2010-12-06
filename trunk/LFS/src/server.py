#!/usr/bin/python
import socket
import threading
import re
import time
from EmailWriter import EmailWriter
from BackUpThread import BackUpThread

host="127.0.0.1"
port=8765
netid="pg298"

# Timer
class Timer(threading.Thread):
    def __init__(self,clientsocket):
        threading.Thread.__init__(self)
        self.currenttime = time.clock()
        self.clientsocket = clientsocket
        self.starttime = time.clock()
        self.timerOn = True
        self.enable = False;
        
    def startTimer(self):
        self.starttime = time.clock()
        self.enable = True
    
    def stopTimer(self):
        self.timerOn = False
        
    def disableTimer(self):
        self.enable = False
        
    def run(self):
        while self.timerOn:
            while self.enable:
                if(time.clock() - self.starttime > 10):
                    self.clientsocket.send("500 TIMEOUT")            
                    self.clientsocket.close()
#                    print "TIMEOUT.. timeout thread is closing connection"
                    return


# handle a single client request
class ConnectionHandler(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__ ( self )
        self.socket = socket
        self.timer = Timer(socket)
        
    def checkHelo(self, msg):
        if msg.startswith("HELO "):
            return True
        else:
            return False
    
    def checkMailFrom(self, msg):
        global re_mf
        
        if re_mf.match(msg):
            return True
        else:
            return False
    
    def checkMailTo(self, msg):
        global re_mt
        
        if re_mt.match(msg):
            return True
        else:
            return False
    
    def checkDataMsg(self, msg):
        return (msg=="DATA\n") | (msg=="DATA\r\n") 
    
    def run(self):
        global email_writer
        global backup_writer
        
        self.timer.startTimer()
        self.timer.start()
        
        # Helo
        flag = False
        while not flag:
            msg = ""
            while not msg.endswith("\n"):
                msg += self.socket.recv(1)
#            print msg
            flag = self.checkHelo(msg)
            if not flag:
                self.socket.send("500 Error in Helo msg\n")
        self.timer.disableTimer()
        self.socket.send("200 HELO %s\n" %  netid)
              
              
        # Mail from  
        flag = False
        self.timer.startTimer()
        while not flag:
            msg = ""
            while not msg.endswith("\n"):
                msg += self.socket.recv(1)
#            print msg
            flag = self.checkMailFrom(msg)
            if not flag:
                self.socket.send("500 Error in senderemail:\n")
        self.timer.disableTimer()
        self.socket.send("200 OK\n")
              
        
        # Mail To
        flag = False
        self.timer.startTimer()
        while not flag:
            msg =""
            while not msg.endswith("\n"):
                msg += self.socket.recv(1)
#            print msg
            flag = self.checkMailTo(msg)
            if not flag:
                self.socket.send("500 Error in receiveremail:\n")
        mailto = msg[9:]
        self.timer.disableTimer()
        self.socket.send("200 OK\n")
                      
              
        # Data
        flag = False
        self.timer.startTimer()
        while not flag:
            msg =""
            while not msg.endswith("\n"):
                msg += self.socket.recv(1)
#            print msg
            flag = self.checkDataMsg(msg)
            if not flag:
                self.socket.send("500 Error expecting DATA\n")
        self.timer.disableTimer()
        self.socket.send("354 START YOUR MESSAGE AND END WITH A PERIOD ON A LINE BY ITSELF\n")
        
        # Handle Email Msg
        flag = False
        msg = ""
        self.timer.startTimer()
        while not flag:
            msg += self.socket.recv(1024)
            if msg.endswith("\n.\n") | msg.endswith("\r\n.\r\n"):
                flag = True
#        print msg
        self.timer.disableTimer()
        self.socket.send("200 OK\n")
        
        email_writer.write(msg, mailto)
        
        backup_writer.newMsg()
        
        self.socket.close()
    
    
# the main server loop
def serverloop():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # mark the socket so we can rebind quickly to this port number 
    # after the socket is closed
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to the local loopback IP address and special port
    serversocket.bind((host, port))
    # start listening with a backlog of 256 connections
    serversocket.listen(256)

    while True:
        # accept a connection
        (clientsocket, address) = serversocket.accept()
#        print "connection accepted"
        ct = ConnectionHandler(clientsocket)
        ct.start()



email_writer = EmailWriter()
backup_writer = BackUpThread()
backup_writer.start()
re_mf = re.compile('MAIL FROM: [\S]+@[\S]+\.[\S]+')
re_mt = re.compile('RCPT TO: [\S]+@[\S]+\.[\S]+')

print "Server coming up... port=%d" % port
serverloop()
