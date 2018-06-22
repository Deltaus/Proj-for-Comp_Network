#Skeleton   Python Code for the	Web Server	
#import socket module
from socket import *
import time
import sys # In order to terminate the program

MSG_PREFIX_LENGTH = 5
BUFFER_MAXSIZE = 2048

def recvx(socket, msgLen):
    
    print("Message length: " + str(msgLen))    
    total_recv = 0
    chunks = []
    while total_recv != msgLen:
        chunk = socket.recv(min(msgLen - total_recv, BUFFER_MAXSIZE))
        if chunk == b'':
            break
        total_recv += len(chunk)
        chunks.append(chunk)
        
    return b''.join(chunks)

def recvData(socket):

    body_length = int(recvx(socket, MSG_PREFIX_LENGTH).decode())
    
    return recvx(socket, body_length)

def recvData2(socket):
    
    data = socket.recv(BUFFER_MAXSIZE)
    
    return data

    
def completeMsg(msg):
    
    global MSG_PREFIX_LENGTH
    
    bytes_body_length = str(len(msg)).encode()
    bytes_body_length = b'0' * (MSG_PREFIX_LENGTH - len(bytes_body_length)) + bytes_body_length
    msg = bytes_body_length + msg
    
    return msg

def sendData(socket, msg):
    
    msg = completeMsg(msg)
    msg_length = len(msg)
    total_sent = 0
    while total_sent != msg_length:
        sent = socket.send(msg[total_sent:])
        if sent == 0:
            break
        total_sent += sent

def readFile(filename, filetype):
    
    if filetype == 'html':
        msgType = b"Content-Type: html\r\n"
        try:
            with open(filename, 'r') as f:
                outputdata = f.read()
            headerState = b"HTTP/1.1 200 OK\r\n"
        except IOError:
            outputdata = "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n"
            headerState = b"HTTP/1.1 404 Not Found\r\n"
            print("?????Cant't find page!?????")
            
    elif filetype == 'txt':
        msgType = b"Content-Type: text\r\n"
        try:
            f = open(filename, 'r')
            outputdata = f.read()
            f.close()
            headerState = b"HTTP/1.1 200 OK\r\n"
        except IOError:
            outputdata = ""
            headerState = b"HTTP/1.1 404 Not Found\r\n"
            print("?????Cant't find text file!?????")
        
    elif filetype == 'jpg':
        msgType = b"Content-Type: image\r\n"
        try:
            f = open(filename, 'rb')
            outputdata = f.read()
            f.close()
            headerState = b"HTTP/1.1 200 OK\r\n"
        except IOError:
            outputdata = b""
            headerState = b"HTTP/1.1 404 Not Found\r\n"
            print("?????Cant't find image file!?????")
    else:
        msgType = b"Content-Type: unknown\r\n"
        outputdata = ""
        headerState = b"HTTP/1.1 404 Not Found\r\n"

    return msgType, outputdata, headerState

#set up encoding
if sys.getdefaultencoding() != 'utf-8':
    imp.reload(sys)
    sys.setdefaultencoding('utf-8')

serverSocket = socket(AF_INET, SOCK_STREAM)

#Prepare a sever socket
serverSocket.bind(('', 12000))
serverSocket.listen(100)
#Connection counter
count = 0

while True:
    #Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    print("Connection built...")
    flag = 1
    while flag:
        
        try:
            try:
                print("#Receiving data...")
                message = recvData(connectionSocket)
            except socket.timeout:
                message = b""
        except TypeError:
            message = b""
        except IndexError:
            print("#No data received...")           
            break
        
        if len(message) != 0:
            print("\nConnected by: " + str(addr))
            print("Request is :\n" + message.decode() + "\n")
            #Parse request
            msgRecv = message.decode().split()
            filename = msgRecv[1]
            print("#File Name: " + filename)
            filetype = filename.split('.')[-1]
            print("#Request Type: " + filetype)
            conPos = msgRecv.index("Connection:")
            connType = msgRecv[conPos+1]
            print("#Connection Type: " + connType)
            if connType == "Keep-Alive":
                flag = 1
                headerConnect = b"Connection: Keep-Alive\r\n"
            else:
                flag = 0
                headerConnect = b"Connection: close\r\n"
                
            headerType, headerData, headerState = readFile(filename, filetype)
            print("HeaderState is: " + headerState.decode())
            if filetype != 'jpg':
                headerData = headerData.encode()
            
            response = headerState + headerType + headerConnect + headerData
            print("#Sending response...")
            msg = completeMsg(response)
            try:
                connectionSocket.sendall(msg)
            except ConnectionResetError:
                break
            print("#Response sent...")
                  
        else:
            break
        
    connectionSocket.close() 
    print("Connection closed...")
    
serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data


