from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.topolib import TreeTopo
from mininet.topo import SingleSwitchTopo
from mininet.topo import LinearTopo
import threading
import os
import time
#import iperf
import Queue
import sys
import json
q = Queue.Queue()
port = 5789

class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts."
    def __init__(self, n=2, **opts):
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        for h in range(n):
            #Each host gets 50%/n of system CPU
            host = self.addHost('h%s' % (h + 1), cpu=.5/n)
            #10 Mbps, 5ms delay, 0% Loss, 1000 packet queue
            #self.addLink(host, switch,delay='0ms', loss=0, max_queue_size=1000, use_htb=True)
            self.addLink(host, switch)

class FatTreeTopo(Topo):
    "Fat-tree topology"
    def __init__(self):
        Topo.__init__(self)
        ##Core Layer
        coreSwitches = []
        for i in range(4):
            switch = self.addSwitch('100' + str(i+1))
            coreSwitches.append(switch)
        print "core sw:"
        print coreSwitches
        ##Aggregation Layer
        aggrSwitches = []
        for i in range(8):
            switch = self.addSwitch('200' + str(i+1))
            aggrSwitches.append(switch)
        print "aggregate sw:"
        print aggrSwitches
        ##Edge Layer
        edgeSwitches = []
        for i in range(8):
            switch = self.addSwitch('300' + str(i+1))
            edgeSwitches.append(switch)
        print "edge sw:"
        print edgeSwitches
        ##Hosts
        hosts = []
        for i in range(16):
            host = self.addHost(str(i))
            hosts.append(host)
        print "hosts:"
        print hosts
        ##Links between core layer and aggregate layer
        csNum = len(coreSwitches)
        evenAggrSwitches = []
        oddAggrSwitches = []
        for s in aggrSwitches:
            #print type(s)
            #print s
            if int(s[-1]) % 2 == 0:
        	evenAggrSwitches.append(s)
            else:
        	oddAggrSwitches.append(s)
        print 'number of even: %d'%len(evenAggrSwitches)
        print evenAggrSwitches
        print 'number of odd: %d'%len(oddAggrSwitches)
        print oddAggrSwitches
        for cs in range(csNum):
            if cs < csNum / 2:
        	for ss in oddAggrSwitches:
         	    #self.addLink(coreSwitches[cs], s, delay='0ms', loss=0, max_queue_size=1000, use_htb=True)
                    self.addLink(coreSwitches[cs], ss)
            else:
                for ss in evenAggrSwitches:
         	    #self.addLink(coreSwitches[cs], s, delay='0ms', loss=0, max_queue_size=1000, use_htb=True)
                    self.addLink(coreSwitches[cs], ss)

        ##Links between aggregate layer and edge layer
        for ss in aggrSwitches:
            index = int(ss[-1]) - 1
            print 'aggr index : %d'%index
            if index % 2 == 0:
       		#self.addLink(s, edgeSwitches[index], delay='0ms', loss=0, max_queue_size=1000, use_htb=True)
       		self.addLink(ss, edgeSwitches[index])
                #self.addLink(s, edgeSwitches[index+1], delay='0ms', loss=0, max_queue_size=1000, use_htb=True)
                self.addLink(ss, edgeSwitches[index+1])
            else:
       		#self.addLink(s, edgeSwitches[index], delay='0ms', loss=0, max_queue_size=1000, use_htb=True)
                self.addLink(ss, edgeSwitches[index])
       		#self.addLink(s, edgeSwitches[index-1], delay='0ms', loss=0, max_queue_size=1000, use_htb=True)
                self.addLink(ss, edgeSwitches[index-1])

        ##Links between edge layer and hosts
        for es in edgeSwitches:
            index = int(es[-1]) - 1
            #self.addLink(es, hosts[index * 2], delay='0ms', loss=0, max_queue_size=1000, use_htb=True)
            self.addLink(es, hosts[index * 2])
            #self.addLink(es, hosts[index * 2 + 1], delay='0ms', loss=0, max_queue_size=1000, use_htb=True)
            self.addLink(es, hosts[index * 2 + 1])

def enableSW():

    for i in range(4):
        cmd = "ovs-vsctl set bridge %s stp_enable=true"%('100' + str(i+1))
        os.system(cmd)
        print "core %s enabled"%('100' + str(i+1))
    for i in range(8):
        cmd = "ovs-vsctl set bridge %s stp_enable=true"%('200' + str(i+1))
        os.system(cmd)
        print "aggr %s enabled"%('200' + str(i+1))
    for i in range(8):
        cmd = "ovs-vsctl set bridge %s stp_enable=true"%('300' + str(i+1))
        os.system(cmd)
        print "edge %s enabled"%('300' + str(i+1))

def pingTwoHosts100Times(h1, h2):

    global q

    func_name = sys._getframe().f_code.co_name
    startTime = time.time()
    for iter in range(100):
    	h1.cmd("ping -c 1 %s"%(h2))
    endTime = time.time()

    q.put((round(endTime-startTime, 3) * 1000, func_name))

    return round(endTime - startTime, 3) * 1000


def run100MBTraffic(h1, h2):

    global q, port

    func_name = sys._getframe().f_code.co_name

    port = port + 1

    client, server = h2, h1
    #server.cmd( 'killall -9 iperf' )
    iperfArgs1 = 'iperf -s -p %d -i 1' % port
    server.popen( iperfArgs1 )
    iperfArgs2 = 'iperf -p %d' % port
    startTime = time.time()
    client.popen( iperfArgs2 + ' -c ' + server.IP() + ' -b 80m -t 10')
    endTime = time.time()

    q.put((round(endTime-startTime,3) * 1000, func_name))

    return round(endTime - startTime, 3) * 1000


def timeMeasure(hosts, q):

    print "######## Ping 100 times between each pair ########"
    mTime = dict()
    for h1 in hosts:
    	for h2 in hosts:
    	    if h1 != h2:
    		t = pingTwoHosts100Times(h1, h2)
    		mTime[str(h1.name) + '->' + str(h2.name)] = ['' , '', ['', '']]
    		mTime[str(h1.name) + '->' + str(h2.name)][0] = str(t) + 'ms'
    
    print "######## 100MB iperf transmission ########"
    #iperfTime = dict()
    for h1 in hosts:
    	for h2 in hosts:
    	    if h1 != h2:
    		t = run100MBTraffic(h1, h2)
  		mTime[str(h1.name) + '->' + str(h2.name)][1] = str(t) + 'ms'

    print "######## Run two tests at the same time ########"
    #simulTime = dict()
    for h1 in hosts:
    	for h2 in hosts:
    	    if h1 != h2:
    		result = []
    		t1 = threading.Thread(target=pingTwoHosts100Times, name='ping', args=(h1, h2, ))
    		t2 = threading.Thread(target=run100MBTraffic, name='iperf', args=(h1, h2, ))
    		t1.start()
    		t2.start()
    		t1.join()
    		t2.join()
                while not q.empty():
                    result.append(q.get())
                with q.mutex:
    		    q.queue.clear()
                for r in result:
                    if r[1] == pingTwoHosts100Times.__name__:
                	mTime[str(h1.name) + '->' + str(h2.name)][2][0] = str(r[0]) + 'ms'
                    else:
               		mTime[str(h1.name) + '->' + str(h2.name)][2][1] = str(r[0]) + 'ms'

    return mTime


def write2file(data, path):
    
    with open(path, 'w') as writef:
        l = json.dumps(data)
        writef.write(l)


def elephantMiceTest():

    global q

    print "********** Fat Tree Topo **********"
    fatTreeTopo = FatTreeTopo()
    ftNet = Mininet(topo=fatTreeTopo)
    ftNet.start()
    enableSW()
    #os.system("ovs-vsctl set Bridge switch stp_enable=true")
    print "Testing network connectivity"
    ftNet.pingAll()
    hosts = ftNet.hosts
    ftt = timeMeasure(hosts, q)
    ftNet.stop()
    os.system("sudo mn -c")
    print "Writing..."
    path0 = "./fatTreeTopo.json"
    write2file(ftt, path0)

    print "********** Simple Topo **********"
    simpleTopo = SingleSwitchTopo(n=16)
    #spNet = Mininet(topo=simpleTopo, host=CPULimitedHost, link=TCLink)
    spNet = Mininet(topo=simpleTopo)
    spNet.start()
    print "Testing network connectivity"
    spNet.pingAll()
    hosts = spNet.hosts
    spt = timeMeasure(hosts, q)
    spNet.stop()
    os.system("sudo mn -c")
    print "Writing..."
    path1 = "./simpleTopo.json"
    write2file(spt, path1)

    print "********** Linear Topo **********"
    linearTopo = LinearTopo(k=16, n=1)
    #lnNet = Mininet(topo=linearTopo, host=CPULimitedHost, link=TCLink)
    lnNet = Mininet(topo=linearTopo)
    lnNet.start()
    print "Testing network connectivity"
    lnNet.pingAll()
    hosts = lnNet.hosts
    lnt = timeMeasure(hosts, q)
    lnNet.stop()
    os.system("sudo mn -c")
    print "Writing..."
    path2 = "./linearTopo.json"
    write2file(lnt, path2)

    print "Finished."
   
 
if __name__=='__main__':
    setLogLevel('info')
    ##perfTest1()
    elephantMiceTest()
