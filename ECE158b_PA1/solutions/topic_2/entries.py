#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  7 16:00:28 2018

@author: deltau
"""

import random
import threading
import time
import numpy

###############Class definition#################
class Tracker:
    
    #IPaddress: state
    peerList = dict()
    
    def __init__(self, peerList):
        for ip in peerList:
            self.peerList[ip] = 1
        
    def insertPeer(self, ipAddr):
        
        if ipAddr in self.peerList: 
            print("Peer already exist!")
            self.peerList[ipAddr] = 1
        else:
            self.peerList[ipAddr] = 1
            print("Successfully added!")
            
    def deletePeer(self, ipAddr):
        
        if ipAddr in self.peerList:
            del self.peerAddr[ipAddr]
        else:
            print("Peer doesn't exist!")
            
    def checkState(self, ipAddr):
        
        return self.peerList[ipAddr]
    
    def allocatePeers(self):
        
        peerNum = len(self.peerList)
        alloNum = max(int(peerNum * 0.25), 4)
        allocated = random.sample(list(self.peerList), alloNum)
        
        return allocated
    
        
class Peer(threading.Thread):
    
    IP = ''
    index = 0
    peerList = dict()
    top4 = list()  
    fileChunks = set()
    fileSize = 0
    flag = -1
    totalSpeed = 0
    downPercent = 0

    def __init__(self, IP):
        
        threading.Thread.__init__(self)
        self.IP = IP
        
    def run(self):
        
        print(threading.current_thread().name + " is at " + self.IP)
        while self.fileSize > len(self.fileChunks):
            
            if self.flag == -1:
                # set download speed
                spd0 = 0
                for p in self.top4:
                    spd0 += self.getSpeed(speedMat, peers[p].getIPAddr())
                for p in self.top4:
                    spd = self.getSpeed(speedMat, peers[p].getIPAddr())
                    if spd0 > DLSPEEDMAX:
                        spd *= (DLSPEEDMAX/spd0)
                    cks = peers[p].uploadChunks(self.fileChunks, int(spd/CHUNKSIZE))
                    self.downloadChunks(cks)
                    self.check()
            elif self.flag == 0:
                self.flag = 1
            else:
                pass
            time.sleep(0.5)
        
        threadLock.acquire()
        print(threading.current_thread().name + " Lock acquired!")
        imDone()
        threadLock.release()
        print(threading.current_thread().name + " Lock released!")
        print(threading.current_thread().name + " finished.")
        
    # Join one bit network
    def joinNetwork(self, tracker):
        
        tracker.insertPeer(self.IP)
    
    # Set top 4 peers    
    def setTop4(self):
        
        self.peerList = dict(sorted(self.peerList.items(), key=lambda item:item[1], reverse=True))
        self.top4 = list(self.peerList)[:4]
        self.totalSpeed = 0
        for p in self.top4:
            self.totalSpeed += self.peerList[p]
     
    # Measure speeds of all peers on the list
    def measureSpeed(self, speedMat):
        
        self.index = int(self.IP.split('.')[-1]) - 1
        for p in self.peerList:
            pindex = int(p.split('.')[-1]) - 1
            self.peerList[p] = speedMat[pindex][self.index]
    
    # File size        
    def setFileSize(self, size):
    
        self.fileSize = size
        
    def initFileChunks(self, perc=1):
        
        num = int(round(self.fileSize * perc))
        if self.fileSize != 0:
            temp = range(self.fileSize)
            self.fileChunks = set(random.sample(temp, num))
        else:
            print("Empty file targeted.")
            
        return self.fileChunks
    
    def initFileChunks2(self, chunks):
        
        self.fileChunks = chunks
        
    # Upload chunks to other peers
    def uploadChunks(self, chunkList, num):
        
        undl = self.fileChunks - chunkList
        
        if len(undl) == 0:
            return set([-1])    
        if len(undl) > num:
            ready = set(random.sample(undl, num))
            return ready
        else:
            return undl
    
    # Download chunks from other peers
    def downloadChunks(self, chunkList):
        
        if chunkList == [-1]:
            #print("No chunks to download...")
            pass
        else:
            self.fileChunks = set(list(self.fileChunks) + list(chunkList))
            self.downPercent = min(round(len(self.fileChunks)/self.fileSize * 100,2), 100.0)
            if len(self.fileChunks) == self.fileSize:
                self.flag = 0
                
    def check(self):
        
        if len(self.fileChunks) == self.fileSize:
                self.flag = 0
            
    # Get peer list from the tracker    
    def getPeerList(self, peerList):
        
        for p in peerList:
            self.peerList[p] = 0        
       
    # Return IP address        
    def getIPAddr(self):
        
        return self.IP
    
    
    # Return sum of speeds of top4 peers
    def getTotalSpeed(self):
        
        return self.totalSpeed
    
    def getPercent(self):
        
        return self.downPercent
    
    # Get the spped between a specific peer
    def getSpeed(self, speedMat, ipAddr):
        
        index = int(ipAddr.split('.')[-1]) - 1
        
        return int(round(speedMat[index][self.index]))
    
    # Try a new peer
    def tryNew(self, speedMat):
        
        peer = random.choice(list(self.peerList))
        self.peerList[peer] = self.getSpeed(speedMat, peer)
        self.setTop4()
        
#######################Parameters###########################        
threadLock = threading.Lock()        
PEERDONE = 0        
ipNetAddr = '10.0.0.'
UPPERBOUND = 1500     # Max download speed 5.0Mb/s
LOWERBOUND = 300      # Min download speed 0.5Mb/s
hostNum = 50         # Number of peers, 10.0.0.1 - 10.0.0.x
INTERVAL = 8         # Time interval
FILESIZE = 500 * 1024 # File size 500 Mb
CHUNKSIZE = 256       # Chunk size 256 Kb
FILECHUNKS = range(int(FILESIZE / CHUNKSIZE) + 1) # Chunks
PEERDONE = 0
INITPERCT = 0.2       
        
#ULSPEEDMAX = 3000
DLSPEEDMAX = 6000
#######################Functions############################       
# Reset speeds every 8 sec(= INTERVAL) 
spdCount = 0 
def measureSpeed():
    
    global speedMat, hostNum, PEERDONE, peers, spdCount
    
    print("Start measuring speeds...")
    while True:
        
        if PEERDONE == hostNum:
            break
        
        speedMat = numpy.random.randint(LOWERBOUND, UPPERBOUND, size=(hostNum, hostNum))

        for i in range(hostNum):
            speedMat[i][i] = 0
        #######Free riders#######
#        for row in indexFR:
#            for col in hostNum:
#                speedMat[row][col] = 0
        #########################
        for p in peers:
            peers[p].measureSpeed(speedMat)
        spdCount += 1
        print("Speed Measure " + str(spdCount) + " completed.")
        time.sleep(INTERVAL)
            
    print("Transfer terminated, stop measuring speeds.")
            
# Try a new every 30 sec 
tryCount = 0       
def tryNew():
    
    global speedMat, PEERDONE, peers, tryCount
    
    print("Start trying new peers...")
    while True:
        
        if PEERDONE == hostNum:
            break
        
        for p in peers:
            peers[p].tryNew(speedMat)
        tryCount += 1
        print("Trial " + str(tryCount) + " done.")
        time.sleep(INTERVAL * 3)
            
    print("Transfer terminated, stop trying new peers.")

def display():
    
    global peers, PEERDONE
    
    while True:
        
        if PEERDONE == hostNum:
            break
        
        for p in peers:
            print("Peer " + peers[p].getIPAddr() + ", Current speed: " + str(peers[p].getTotalSpeed()) + "Kb/s, " + 
                  str(peers[p].getPercent()) + "% done.")
        print(str(PEERDONE) + " peers done.")
        time.sleep(5)

def imDone():
    
    global PEERDONE
    t = time.time()
    xtime.append(round(startTime - t,3))
    print("I'M DONE!")
    PEERDONE += 1        
        

################################Set up#########################################       
print("Initializing speed matrix...")
speedMat = numpy.random.randint(LOWERBOUND, UPPERBOUND, size=(hostNum, hostNum))            
for i in range(hostNum):
    speedMat[i][i] = 0
print("Done.")

#initialize ip addr
print("Initializing IP address...")
ipList = []
for i in range(1,hostNum+1):   
    ip = ipNetAddr + str(i)
    ipList.append(ip)
print("Done.")

print("Building tracker and peers...")
# Build tracker    
tracker = Tracker(ipList)
# Build peers
peers = dict()
threads = []
lock = threading.Lock()
distributed = set()   
for ip in range(len(ipList)):
    p = Peer(ipList[ip])
    p.getPeerList(tracker.allocatePeers())
    p.measureSpeed(speedMat)
    p.setTop4()
    p.setFileSize(len(FILECHUNKS))
    if ip == len(ipList) - 1:
        p.initFileChunks2(set(FILECHUNKS) - distributed)
    else:
        disCk = p.initFileChunks(perc=INITPERCT)
        distributed = disCk | distributed
    threads.append(p)
    peers[ipList[ip]] = p
print("Done.") 

#################### If you want to join some freeriders##############
## Freeriders
#freeRiders = random.sample(ipList, int(hostNum/4)) 
#indexFR = []
#for fr in freeRiders:
#    ind = fr.split('.')[-1]
#    indexFR.append(ind)
######################################################################

print("\n")
print("--------------DOWNLOADING INFO---------------")
print("File Size:    " + str(FILESIZE/1024) + "Mb")
print("Chunk Size:   " + str(CHUNKSIZE) + "Kb")
print("Chunk Number: " + str(len(FILECHUNKS)) + "chunks")
print("Peer Number:  " + str(hostNum) + "peers")        
        
speedThread = threading.Thread(target=measureSpeed, name='speedMat')
tryThread = threading.Thread(target=tryNew, name='tryNew')
dispThread = threading.Thread(target=display, name='disp')
print("Done.")

xtime = []

print("Start running threads...")
speedThread.start()
tryThread.start()
dispThread.start()
startTime = time.time()
for t in threads:
    t.start()        
for t in threads:
    t.join()
endTime = time.time()
print("Finished! Time: " + str(round(endTime - startTime, 3)) + " seconds.") 
print("Max time: " + str(abs(min(xtime))) + ", Min time: " + str(abs(max(xtime))))
speedThread.join()
tryThread.join()
dispThread.join()      