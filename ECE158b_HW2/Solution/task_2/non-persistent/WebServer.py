#Skeleton   Python Code for the	Web Server	
#import socket module
from socket import *
import sys # In order to terminate the program
#set up encoding
if sys.getdefaultencoding() != 'utf-8':
    imp.reload(sys)
    sys.setdefaultencoding('utf-8')

serverSocket = socket(AF_INET, SOCK_STREAM)

#Prepare a sever socket
#Fill in start
serverSocket.bind(('', 12000))
serverSocket.listen(100)
#serverSocket.setblocking(0)
#Fill in end
count = 0
flag = 0

while True:
    #Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()#Fill in start #Fill in end
    print("Connection " + str(count) + " built")
    count += 1
    try:
        message = connectionSocket.recv(4096)#Fill in start #Fill in end
        print("Connected by: " + str(addr))
        print("Request is :\n" + message.decode())
        msgRecv = message.decode().split()

        filename = msgRecv[1]
        filetype = filename.split('.')[-1]
        print("Filename: " + filename)
        print("Filetype: " + filetype)
        if filetype == 'html':
            msgType = "Content-Type: html\r\n"
            filename = filename.split('/')[-1]
            with open(filename, 'r') as f:
                outputdata = f.read()
        elif filetype == 'txt':
            msgType = "Content-Type: text\r\n"
            filename = 'object_files/txt/'+filename.split('/')[-1]
            f = open(filename, 'r')
            outputdata = f.read()
            f.close()
        elif filetype == 'jpg' or filetype == 'jpeg':
            msgType = "Content-Type: image\r\n"
            filename = 'object_files/pics/'+filename.split('/')[-1]
            f = open(filename, 'rb')
            outputdata = f.read()
            #outputdata = str(outputdata, encoding = "utf-8")
            f.close()
        else:
            msgType = "Content-Type: unknown\r\n"
            outputdata = ""
        if filetype != 'jpg' and filetype != 'jpeg':
            outputdata = outputdata.encode()
        msg = "HTTP/1.1 200 OK\r\n".encode() + msgType.encode() + outputdata + '\r\n'.encode()
        #msg = msg.encode()
        
        connectionSocket.sendall(msg)
        print("Response sent.")
        connectionSocket.close()
        print("Connection closed...")
        
    except IOError:
        # Send HTTP response message for file not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())
        # Close the client connection socket
        connectionSocket.close()
        
serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data


