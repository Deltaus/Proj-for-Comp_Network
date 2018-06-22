#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  7 13:24:33 2018

@author: deltau
"""

import sys
import os
import socket
from socket import AF_INET, SOCK_DGRAM
import imp
import time
from lxml import etree

MSG_PREFIX_LENGTH = 5
BUFFER_MAXSIZE = 2048

def recvx(socket, msgLen):
    
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

#Function 2: Build tcp connections and send requests
def sendRequest(socket, request):

    try:
        #print("#Sending Object request...")
        msg = completeMsg(request)
        socket.sendall(msg)
        #print("#Object Request sent...")       
    except TimeoutError:
        #print("timeout...")
        return "", "",  "Keep_Alive" 
    time.sleep(1)   
    try:
        try:
            #print("#Receiving data...")
            dataRecv = recvData(socket)
        except socket.timeout:
            dataRecv = b""
    except TypeError:
        dataRecv = b""
        
    if len(dataRecv) != 0:
        #print("#Data received...")
        #print("#Start parsing...")
              
        try:
            message = dataRecv.decode().split()
            if 'OK' in message:
                #Mark position of 'Content-Type', in order to locate raw data
                typePos = message.index('Content-Type:')
                connPos = message.index('Connection:')
                fileType = message[typePos+1]
                connType = message[connPos+1]
                #Raw data
                data = message[typePos+2:]
                return ' '.join(data), fileType, connType
            else:
                #print("Error: 404 Not Found.")
                return "", "", "Keep-Alive"
        except UnicodeDecodeError:  
            #No need decoding, split directly
            message = dataRecv.split()
            if b'OK' in message:
                typePos = message.index(b'Content-Type:')
                connPos = message.index(b'Connection:')
                #type
                fileType = message[typePos+1]
                connType = message[connPos+1]
                #Raw data
                data = message[typePos+2:]
                return b" ".join(data), fileType.decode(), connType.decode()
            else:
                #print("Error: 404 Not Found.")
                return b"", "", "Keep-Alive"
            
        #print("#Parsing completed...")
    else:
        #print("#No data received...")
        return "", "", "Keep-Alive"
    
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

#Set up client socket
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
clientHost = socket.gethostname()
clientPort = 12999
clientSocket.bind((clientHost, clientPort))
clientSocket.settimeout(30)
#Set up server info
serverHost = serverIP
serverPort = int(serverPort)

#Request connection
print("Start connecting...")
clientSocket.connect((serverHost, serverPort))

#Build request
headerHost = 'Host: ' + serverHost + ':' + str(serverPort) + '\r\n'
headerAgent = 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36\r\n'
headerAccept = 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\n'
headerEncoding = 'Accept-Encoding: gzip, deflate, br\r\n'
headerLang = 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\n'
headerMethod = 'Get ' + './'+filePath + ' HTTP/1.1\r\n'
headerConnect = 'Connection: Keep-Alive\r\n'
request = headerMethod + headerHost + headerConnect + headerAgent + headerAccept + headerEncoding + headerLang
print("#Request sent:\n" + request)
request = request.encode()

#Send HTML Request
try:
    #print("#Sending HTML request...")
    msg = completeMsg(request)
    clientSocket.sendall(msg)
    #print("#HTML Request sent...")       
except TimeoutError:
    print("timeout...")
#Receive HTML Request
try:
    try:
        #print("#Receiving HTML file...")
        dataRecv = recvData(clientSocket)
    except socket.timeout:
        dataRecv = b""
except TypeError:
    dataRecv = b""

flag = 0
dataRecv = dataRecv.decode()
objectPaths = []
if len(dataRecv) != 0:
                
    filename = filePath.split('/')[-1]
    #Store HTML file
    with open('./download/'+filename, 'w') as f:
        f.write(dataRecv)
    #Parse HTML file
    tree = etree.HTML(dataRecv)
    srcs = tree.xpath('//iframe/@src')
    for p in srcs:
        objectPaths.append(p)
    srcs = tree.xpath('//img/@src')
    for p in srcs:
        objectPaths.append(p)
    #print("###Objects found in HTML file:")
    for obj in objectPaths:
        print("   " + obj)
    flag = 1
else:
    print("Error! No HTML file found. \nClosing connection...")
    clientSocket.close()

######################################
count = 1
retry = 0
while(flag):
    
    if count == 20:
        headerConnect = 'Connection: close\r\n'
    else:
        headerConnect = 'Connection: Keep-Alive\r\n'
        
    print("File count: " + str(count))
    if count <= len(objectPaths):
        headerMethod = 'Get ' + objectPaths[count-1] + ' HTTP/1.1\r\n'
    else:
        time.sleep(5)
        os.system("open ./" + filePath.split('/')[-1])
        clientSocket.close()
        break
        
    #Build request
    request = headerMethod + headerHost + headerConnect + headerAgent + headerAccept + headerEncoding + headerLang
    print("#Request sent:\n" + request)
    request = request.encode()
    
    #Send and receive data
    data, fileType, conType = sendRequest(clientSocket, request)

    if conType == 'Keep-Alive':
        if len(data) != 0:                  
            if fileType == 'text':
                filename = objectPaths[count-1].split('/')[-1]
                #Store object
                with open('./download/'+filename, 'w') as f:
                    f.write(data)  
            else:
                filename = objectPaths[count-1].split('/')[-1]
                #Store object
                with open('./download/'+filename, 'wb') as f:
                    f.write(data) 
        else:
            print("No object received.") 
            
        count += 1   
    #If all done, open HTML file in browser then quit
    else:
        os.system("open ./" + filePath.split('/')[-1])
        clientSocket.close()
        break
