#Skeleton   Python Code for the	Web Server	
#import socket module
from socket import *
import sys # In order to terminate the program
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

serverSocket = socket(AF_INET, SOCK_STREAM)

#Prepare a sever socket
#Fill in start
serverSocket.bind(('', 12000))
serverSocket.listen(5)
#Fill in end

while True:
    #Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()#Fill in start #Fill in end
    try:
        message = connectionSocket.recv(2048)#Fill in start #Fill in end
        filename = message.split()[1]
        print("filename: "+filename[1:].decode())
        f = open(filename[1:])
        outputdata = f.read()#Fill in start #Fill in end
        #Send one HTTP header line into socket
        #Fill in start
        f.close()
        msg = "HTTP/1.1 200 OK\r\n\r\n".encode()
        connectionSocket.send(msg)
        #Fill in end
        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
        connectionSocket.close()
    except IOError:
        # Send HTTP response message for file not found
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
        connectionSocket.send("<html><head></head><body><h1>404 Not Found...</h1></body></html>\r\n".encode())
        # Close the client connection socket
        connectionSocket.close()
 
serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data


