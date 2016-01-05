import sys  #for IP and port passing
import socket
import re   #regular expressions
from Connection import Connection
from FileWorker import*
from SocketWrapper import*
import time
import multiprocessing as mp
import select

class MultiServer:
    def __init__(self,IP,ports):
        self.ports = ports
        self.IP = IP
        self.createSockets()
        

    def createSockInfo(self):
        #servinfo: server socket, client socket, command string, command routine
        self.servInfo = [(TCP_ServSockWrapper(self.IP,self.ports[0]),None,'time'),
                          (TCP_ServSockWrapper(self.IP,self.ports[1]),None,'echo'),
                          (TCP_ServSockWrapper(self.IP,self.ports[2]),None,'download')]
    
    def waitClientQueries(self):
        readable = []
        while True:
            readable = [sock.raw_sock for sockInfo[0] in self.servInfo]
            try:
                readable,writable,exceptional = select.select(readable,[],[]) 
            except OSError:
                continue
            #new client
            for sockInfo in self.servInfo:
                if sockInfo[0].raw_sock in readable:

    
    def acceptNewClient(self,sockInfo):
        sock,addr = servSock.raw_sock.accept()
        sockWrap = SockWrapper(raw_sock=sock,inetAddr=addr)
        #store in clients list
        sockInfo[1] = sockWrap

if __name__ == "__main__":
    
    