#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 17:26:27 2018

@author: deltau
"""

import threading
#import random
#from entries import Tracker
#from entries import Peer
#import numpy
import time

#ipNetAddr = '10.0.0.'
#
#UPPERBOUND = 2500     # Max download speed 5.0Mb/s
#LOWERBOUND = 300      # Min download speed 0.5Mb/s
#hostNum = 10         # Number of peers, 10.0.0.1 - 10.0.0.x
#INTERVAL = 8         # Time interval
#FILESIZE = 500 * 1024 # File size 500 Mb
#CHUNKSIZE = 256       # Chunk size 256 Kb
#FILECHUNKS = range(int(FILESIZE / CHUNKSIZE) + 1) # Chunks
#PEERDONE = 0
#INITPERCT = 0.2


#initial speed matrix
#speedMat[i][j] = speed i -> j
#print("Initializing speed matrix...")
#speedMat = numpy.random.randint(LOWERBOUND, UPPERBOUND, size=(hostNum, hostNum))
#for i in range(hostNum):
#    speedMat[i][i] = 0
#print("Done.")
#
##initialize ip addr
#print("Initializing IP address...")
#ipList = []
#for i in range(1,hostNum+1):   
#    ip = ipNetAddr + str(i)
#    ipList.append(ip)
#print("Done.")
#
#print("Building tracker and peers...")
## Build tracker    
#tracker = Tracker(ipList)
## Build peers
#peers = dict()
#lock = threading.Lock()
#distributed = set()   
#for ip in range(len(ipList)):
#    p = Peer(ipList[ip])
#    p.getPeerList(tracker.allocatePeers())
#    p.measureSpeed(speedMat)
#    p.setTop4()
#    p.setFileSize(len(FILECHUNKS))
#    if ip == len(ipList) - 1:
#        p.initFileChunks2(set(FILECHUNKS) - distributed)
#    else:
#        disCk = p.initFileChunks(perc=INITPERCT)
#        distributed = disCk | distributed
#    peers[ipList[ip]] = p
#print("Done.")    
#
#print("\n")
#print("--------------DOWNLOADING INFO---------------")
#print("File Size:    " + str(FILESIZE/1024) + "Mb")
#print("Chunk Size:   " + str(CHUNKSIZE) + "Kb")
#print("Chunk Number: " + str(len(FILECHUNKS)) + "chunks")
#print("Peer Number:  " + str(hostNum) + "peers")
 
## Reset speeds every 10 sec   
#spdCount = 0 
#def measureSpeed():
#    
#    global speedMat, hostNum, PEERDONE, peers, spdCount
#    
#    print("Start measuring speeds...")
#    while True:
#        
#        if PEERDONE == hostNum:
#            break
#        
#        speedMat = numpy.random.randint(LOWERBOUND, UPPERBOUND, size=(hostNum, hostNum))
#        for i in range(hostNum):
#            speedMat[i][i] = 0
#        for p in peers:
#            peers[p].measureSpeed(speedMat)
#        spdCount += 1
#        print("Speed Measure " + str(spdCount) + " completed.")
#        time.sleep(INTERVAL)
#            
#    print("Transfer terminated, stop measuring speeds.")
#            
## Try a new every 30 sec 
#tryCount = 0       
#def tryNew():
#    
#    global speedMat, PEERDONE, peers, tryCount
#    
#    print("Start trying new peers...")
#    while True:
#        
#        if PEERDONE == hostNum:
#            break
#        
#        for p in peers:
#            peers[p].tryNew(speedMat)
#        tryCount += 1
#        print("Trial " + str(tryCount) + " done.")
#        time.sleep(INTERVAL * 3)
#            
#    print("Transfer terminated, stop trying new peers.")
#
#def display():
#    
#    global peers, PEERDONE
#    
#    while True:
#        
#        if PEERDONE == hostNum:
#            break
#        
#        for p in peers:
#            print("Peer " + peers[p].getIPAddr() + ", Current speed: " + str(peers[p].getTotalSpeed()) + "Kb/s, " + 
#                  str(peers[p].getPercent()) + "% done.")
#        print(str(PEERDONE) + " peers done.")
#        time.sleep(5)
#
#def imDone():
#    
#    global PEERDONE
#    
#    print("I'M DONE!")
#    PEERDONE += 1

# Download chunks 
#def transition(peer):
#    
#    global speedMat, PEERDONE
#    
#    while True:
#        
#        if PEERDONE == hostNum:
#            break
#        
#        if peer.getState() == -1:
#            for p in peer.getTop4():
#                spd = peer.getSpeed(speedMat, peers[p].getIPAddr())
#                cks = peers[p].uploadChunks(peer.getChunks(), int(spd/CHUNKSIZE))
#                peer.downloadChunks(cks)
#                peer.check()
#        elif peer.getState() == 0:
#            peer.setState(1)
#            lock.acquire()
#            imDone()
#            lock.release()
#        else:
#            pass
#        time.sleep(0.5)
#        
#    print(threading.current_thread().name + " finished.")   

# Build threads
print("Start building threads...")
threads = list()
for i in range(hostNum):
    t = threading.Thread(target=transition, args=(peers[ipList[i]],), name='Thread '+str(i))
    threads.append(t)

#speedThread = threading.Thread(target=measureSpeed, name='speedMat')
#tryThread = threading.Thread(target=tryNew, name='tryNew')
#dispThread = threading.Thread(target=display, name='disp')
#print("Done.")

# Run threads
print("Start running threads...")
speedThread.start()
tryThread.start()
dispThread.start()
startTime = time.time()
for t in threads:
    t.start()
# Join threads
#speedThread.join()
#tryThread.join()
#dispThread.join()
for t in threads:
    t.join()
endTime = time.time()
print("Finished! Time: " + str(round(endTime - startTime, 3)) + " seconds.")
  
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    