import sys  #for IP and port passing
import socket
import re   #regular expressions
from FileWorker import*
from SocketWrapper import*
import time
import multiprocessing as mp
import select

# make sockets pickable/inheritable
if sys.platform == 'win32':
    import multiprocessing.reduction

class QueryError(Exception):
    pass

def echo(sock,commandArgs):
    sock.sendMsg(commandArgs)

def asctime(sock,cmd_args):
    print(sock)  
    sock.sendMsg(time.asctime())

def download(sock,fileName):
    fileWorker = FileWorker(sock,fileName,None,0)
    try:
        fileWorker.sendFileInfo()
        fileWorker.sendPacketsTCP()
    except FileWorkerError as e:
         sock.sendMsg(e.args[0])
    else:
        sock.sendMsg('downloaded')


class MultiServer:
    def __init__(self,IP,ports):
        self.ports = ports
        self.IP = IP
        self.createSockInfo()
        #process number = number of services
        self.nProc = len(self.servInfo) 
        self.pool = mp.Pool(processes= self.nProc)

    def createSockInfo(self):
        #servinfo: server socket, client socket, command string
        self.servInfo = [[TCP_ServSockWrapper(self.IP,self.ports[0]),None,'time',asctime],
                          [TCP_ServSockWrapper(self.IP,self.ports[1]),None,'echo',echo],
                          [TCP_ServSockWrapper(self.IP,self.ports[2]),None,'download',download]]

    def parseCommand(self,sockInfo,cmd_msg):
        #check command format
        regExp = re.compile("[A-Za-z0-9_]+ *.*")
        if regExp.match(cmd_msg) is None:
            raise QueryError("invalid command format \"" + cmd_msg + "\"")
        #find pure command
        commandRegEx = re.compile("[A-Za-z0-9_]+")
        #match() Determine if the RE matches at the beginning of the string.
        matchObj = commandRegEx.match(cmd_msg)
        if(matchObj == None):
            #there is no suitable command
            raise QueryError('there is no such command')
        #group()	Return the string matched by the RE
        str_cmd = matchObj.group()
        if sockInfo[2] != str_cmd:
            raise QueryError('command is not implemented')
        #end() Return the ending position of the match
        cmdEndPos = matchObj.end()
        #cut finding command from the commandMes
        args = cmd_msg[cmdEndPos:]
        #cut spaces after command
        args = args.lstrip()
        return (str_cmd,args)

    def getAndParseCommand(self,sockInfo):
        #client sock = sockInfo[1]
        cmdMsg = sockInfo[1].recvMsg()
        return self.parseCommand(sockInfo,cmdMsg)
   
    def waitClientQueries(self):
        readable = []
        while True:
            readable = [sockInfo[0].raw_sock for sockInfo in self.servInfo]
            try:
                readable,writable,exceptional = select.select(readable,[],[]) 
            except OSError:
                continue
            #new client
            for sockInfo in self.servInfo:
                try:
                    if sockInfo[0].raw_sock in readable:
                        #accept client
                        self.acceptNewClient(sockInfo)
                        #sockInfo[1] = client sock
                        str_cmd,cmd_args = self.getAndParseCommand(sockInfo)
                        self.pool.apply_async(sockInfo[3],args=(sockInfo[1],cmd_args))
                except (OSError,QueryError) as e:
                    sockInfo[1].sendMsg(e.args[0])

    def acceptNewClient(self,sockInfo):
        sock,addr = sockInfo[0].raw_sock.accept()
        sockWrap = SockWrapper(raw_sock=sock,inetAddr=addr)
        sockInfo[1] = sockWrap

if __name__ == "__main__":
     server = MultiServer('192.168.1.2',sys.argv[1:])
     server.waitClientQueries()