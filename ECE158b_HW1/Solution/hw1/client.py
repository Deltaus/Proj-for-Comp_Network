import socket
import time

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
# get local machine name
host = socket.gethostname()
# set ports
serPort = 12000
cliPort = 13000
# set addresses
serAddr = ('165.227.25.63', serPort)
cliAddr = (host, cliPort)
# bind port.
s.bind(cliAddr)
# set timeout
s.settimeout(1)
# set package number
packNum = 10
currNum = packNum

# send and receive messages
while currNum > 0:
    # encode content
    msg = str.encode(str(currNum)+" left, "+"total "+str(packNum)+" packs")
    # start counting
    startTime = time.time()
    # send message
    s.sendto(msg, serAddr)
    # try receiving from server
    try:
        data, serAddr = s.recvfrom(1024)
    # if timeout, print message 
    except socket.error:
        print ("timeout...")
    # else print content and rtt
    else:
        recvTime = time.time()
        rtt = round((recvTime-startTime)*1000,3)
        data = data.decode('ascii')
        print ("Server replied: "+data+"   RTT: "+str(rtt)+"ms")
    # pack num - 1   
    currNum = currNum - 1
        
print ("Finished.")
# close socket
s.close()
