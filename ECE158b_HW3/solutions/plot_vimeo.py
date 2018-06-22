#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 10:52:58 2018

@author: deltau
"""

from scapy.all import *
from matplotlib import pyplot as plt
import numpy as np

#.pcap file
youtube_pcap  = '/Users/deltau/MyProjects/SC/Comp_Network/ECE_158b_HW3/solutions/vimeo_cap.pcap'

#collect time
pkts = rdpcap(youtube_pcap)
tm = []
for pkt in pkts:
    if pkt.dst == '8c:85:90:3d:5d:87' and pkt.haslayer('TCP'):
        if pkt.type == 2048:
            tm.append(pkt.time)
    
timeSec = int(tm[0])
tm = [t-timeSec for t in tm]
startTime = tm[0]
endTime = tm[-1]
#total time, a quantum = 0.2sec
numSlot = round((endTime - startTime)/0.2)
#timePoint = [0, 1, 2, ... , numSlot-1]
timePoint = [i for i in range(numSlot)]
#initialize count list
numPkts = [0 for i in range(numSlot)]
#build a dictionary
pktCount = dict(zip(timePoint, numPkts))
#count
for t in tm:
    ind = int(t/0.2)
    if not ind in pktCount:
        pktCount[ind] = 0
        timePoint.append(ind)
    pktCount[ind] += 1

timePoint = sorted(timePoint)
pC = []
#get the number
for i in pktCount:
    pC.append(pktCount[i])

#plot
fig = plt.figure() 
plt.bar(timePoint, pC,width = 4.5,color = 'green')  
plt.show() 