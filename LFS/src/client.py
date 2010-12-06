#!/usr/bin/python
import sys
import socket
import datetime
import threading

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
toaddr = sys.argv[3] if len(sys.argv) > 3 else "prac@hotmail.com"
fromaddr = sys.argv[4] if len(sys.argv) > 4 else "nobody@example.com"

class MsgSender(threading.Thread):
    def __init__(self, msgid, hostname, portnum, sender, receiver):
        threading.Thread.__init__ ( self )
        self.msgid = msgid
        self.host = hostname
        self.port = portnum
        self.fromaddr = sender
        self.toaddr = receiver
        
    def run(self):
        self.sendmsg(self.msgid, self.host, self.port, self.fromaddr, self.toaddr)
        
    def sendmsg(self, msgid, hostname, portnum, sender, receiver):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        s.connect((hostname, portnum))
    
        s.send("HELO %s\n" % socket.gethostname())
        recv = s.recv(500)
        assert recv == "200 HELO pg298\n", "Something went wrong. Received from server %s" % recv
            
    
        s.send("MAIL FROM: %s\n" % sender)
        recv = s.recv(500)
        assert recv == "200 OK\n", "Something went wrong. Received from server %s" % recv
    
        s.send("RCPT TO: %s\n" % receiver)
        recv = s.recv(500)
        assert recv == "200 OK\n", "Something went wrong. Received from server %s" % recv
    
        s.send("DATA\nContents_of_message_end_here\n.\n")
        recv = s.recv(500)
        assert recv == "354 START YOUR MESSAGE AND END WITH A PERIOD ON A LINE BY ITSELF\n", "Something went wrong. Received from server %s" % recv
        recv = s.recv(500)
        assert recv == "200 OK\n", "Something went wrong. Received from server %s" % recv


for i in range(1, 2):
    print "creating %d connection" % i
    msgSender = MsgSender(i, host, port, fromaddr, toaddr)
    msgSender.start()
