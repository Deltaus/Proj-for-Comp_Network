#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  2 17:20:32 2018

@author: deltau
"""

import sys
import os
import socket
from socket import AF_INET, SOCK_DGRAM
import imp
import time
from lxml import etree

#Function 1: Receive entire data from socket
def recvData(socket):
    
    buffer = b""
    while True:
        dataSeg = socket.recv(4096)
        #If dataSeg is empty then transmission terminated, break
        if not dataSeg:
            break
        #Keep on receiving data
        buffer += dataSeg
        
    return buffer

#Function 2: Build tcp connections and send requests
def tcpConnection(socket, request):

    try:
        print("Trying sending data...")
        socket.sendall(request)
        dataRecv = recvData(socket)
        try:
            #Try decoding data received
            message = dataRecv.decode().split()
            print(message[:5])
            if '200' in message:
                #Mark position of 'Content-Type', in order to locate raw data
                typePos = message.index('Content-Type:')
                #File type
                fileType = message[typePos+1]
                #Raw data
                data = message[typePos+2:]
                #Return decoded data and file type
                return ' '.join(data), fileType
            #Else not found
            else:
                print("404 Error...")
                #Return nothing
                return '', ''
        #When decoding files in bytes, throw exceptions
        except UnicodeDecodeError:  
            #No need decoding, split directly
            message = dataRecv.split()
            if '200'.encode() in message:
                #Mark position of 'Content-Type', in order to locate data
                typePos = message.index('Content-Type:'.encode())
                #File type
                fileType = message[typePos+1]
                #Raw data
                data = message[typePos+2:]
                #Concat byte data
                data = b' '.join(data)
                #Return raw data and file type
                return data, fileType.decode()
            #Else not found
            else:
                print("404 Error...")
                #Return nothing
                return '', ''
    #Throw timeout error        
    except TimeoutError:
        print("timeout...")
        return '', ''
    
#####################PROGRAM STARTS HERE#############################        
#Set up encoding
if sys.getdefaultencoding() != 'utf-8':
    imp.reload(sys)
    sys.setdefaultencoding('utf-8')

#Parse args
args = str(sys.argv).split()
serverIP = args[1]
serverPort = args[2]
filePath = args[3]
serverIP = serverIP[1:len(serverIP)-2]
serverPort = serverPort[1:len(serverPort)-2]
filePath = filePath[1:len(filePath)-2]
folderPath = '/'.join(filePath.split('/')[:-1])

#Set up server info
serverHost = serverIP
serverPort = int(serverPort)

#Build request
headerHost = 'Host: ' + serverHost + ':' + str(serverPort) + '\r\n'
headerConnect = 'Connection: close\r\n'
headerAgent = 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36\r\n'
headerAccept = 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n'
headerEncoding = 'Accept-Encoding: gzip, deflate, br\r\n'
headerLang = 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\n'

#Build connections
count = 0
retry = 0
clientPort = 12999
objectPaths = []
while(True):
    #Set up client socket
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    clientHost = socket.gethostname()
    clientPort = clientPort + 1
    clientSocket.bind((clientHost, clientPort))
    clientSocket.settimeout(24)
    
    #Request connection
    clientSocket.connect((serverHost, serverPort))
    #Get HTML or objects
    print("File Count: " + str(count))
    #HTML file
    if count == 0:
        headerMethod = 'Get ' + './'+filePath + ' HTTP/1.1\r\n'
    #Other objects
    else:
        headerMethod = 'Get ' + objectPaths[count-1] + ' HTTP/1.1\r\n'
    #Build request
    request = headerMethod + headerHost + headerConnect + headerAgent + headerAccept + headerEncoding + headerLang
    print("Request sent:\n" + request)
    request = request.encode()
    
    #Build connections, send and receive data
    data, fileType = tcpConnection(clientSocket, request)
    
    #If data isn't empty
    if len(data) != 0:
        #If it's a HTML file, search all objects' paths
        if fileType == 'html':
            #Get HTML filename
            filename = filePath.split('/')[-1]
            #Store HTML file
            with open('./download/'+filename, 'w') as f:
                f.write(data)
            #Parse HTML file
            tree = etree.HTML(data)
            #Find all src paths
            srcs = tree.xpath('//iframe/@src')
            for p in srcs:
                objectPaths.append(p)
            srcs = tree.xpath('//img/@src')
            for p in srcs:
                objectPaths.append(p)
            print("Objects found in HTML file:")
            for obj in objectPaths:
                print(obj)
        #If it's objects, store them in folder
        elif fileType == 'text':
            #Get filename
            filename = objectPaths[count-1].split('/')[-1]
            #Store object
            with open('./download/'+filename, 'w') as f:
                f.write(data)  
        else:
            filename = objectPaths[count-1].split('/')[-1]
            #Store object
            with open('./download/'+filename, 'wb') as f:
                f.write(data) 
    #If it's empty            
    else:
        if retry < 3:
            clientSocket.close()
            retry += 1
            continue
    count += 1 
    clientSocket.close()
    time.sleep(0.01)
    #If all done, open HTML file in browser then quit
    if count == len(objectPaths) + 1:
        os.system("open ./download/" + filePath.split('/')[-1])
        break
