from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.topolib import TreeTopo
from mininet.topo import SingleSwitchTopo
from mininet.topo import LinearTopo
import os
import time
 
class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts."
    def __init__(self, n=2, **opts):
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        for h in range(n):
            #Each host gets 50%/n of system CPU
            host = self.addHost('h%s' % (h + 1), cpu=.5/n)
            #10 Mbps, 5ms delay, 0% Loss, 1000 packet queue
            self.addLink(host, switch,delay='0ms', loss=0, max_queue_size=1000, use_htb=True)

 
def perfTest():
    "Create network and run simple performance test"
    ssTopo = SingleSwitchTopo(n=4)
    #lnTopo = LinearTopo(k=4, n=1)
    #trTopo = TreeTopo(depth=2, fanout=2)
    ssNet = Mininet(topo=ssTopo,host=CPULimitedHost, link=TCLink)
    #lnNet = Mininet(topo=lnTopo,host=CPULimitedHost, link=TCLink)
    #trNet = Mininet(topo=trTopo,host=CPULimitedHost, link=TCLink)

    print "###############Single Switch Topo###############"    
    print "Testing single switch topo:"
    ssNet.start()
    print "Dumping host connections"
    dumpNodeConnections(ssNet.hosts)
    print "Testing network connectivity"
    ssNet.pingAll()
    print "Ping between hosts:"
    for host1 in ssNet.hosts:
        for host2 in ssNet.hosts:
            if host1 != host2:
                startTime = time.time()
                host1.cmd("ping -c 1 %s"%(host2))
                endTime = time.time()
                print host1.name+"->"+host2.name
                print "RRT: "+str((endTime-startTime)*1000)+"ms"
                #os.system("sudo mn --test cli")
                #os.system("%s ping -c 1 %s"%(host1.name, host2.name))
    print "Testing bandwidth between every pair of hosts:"
    print "Toal host number: "+str(len(ssNet.hosts))
    #h1, h4 = net.get('h1', 'h4')
    for i in range(len(ssNet.hosts)):
        for j in range(i+1, len(ssNet.hosts)):
            ha, hb = ssNet.get('h'+str(i+1), 'h'+str(j+1))
            ssNet.iperf((ha, hb))
    ssNet.stop()
    os.system("sudo mn -c")
    
    print 
    print "#################Linear Topo#####################"
    lnTopo = LinearTopo(k=4, n=1)
    lnNet = Mininet(topo=lnTopo,host=CPULimitedHost, link=TCLink)
    print "Testing linear topo:"
    lnNet.start()
    print "Dumping host connections"
    dumpNodeConnections(lnNet.hosts)
    print "Testing network connectivity"
    lnNet.pingAll()
    print "Ping between hosts:"
    for host1 in lnNet.hosts:
        for host2 in lnNet.hosts:
            if host1 != host2:
                startTime = time.time()
                host1.cmd("ping -c 1 %s"%(host2))
                endTime = time.time()
                print "RRT: "+str((endTime-startTime)*1000)+"ms"
    print "Testing bw between every pair of hosts:"
    print "Total host number: "+ str(len(lnNet.hosts))
    for i in range(len(lnNet.hosts)):
        for j in range(i+1, len(lnNet.hosts)):
            ha, hb = lnNet.get('h'+str(i+1), 'h'+str(j+1))
            lnNet.iperf((ha, hb))
    lnNet.stop()
    os.system("sudo mn -c")

    print 
    print "#################Tree Topo#######################"
    trTopo = TreeTopo(depth=2, fanout=2)
    trNet = Mininet(topo=trTopo,host=CPULimitedHost, link=TCLink)
    print "Testing tree topo:"
    trNet.start()
    print "Dumping host connections"
    dumpNodeConnections(trNet.hosts)
    print "Testing network connectivity"
    trNet.pingAll()
    print "Ping between hosts:"
    for host1 in trNet.hosts:
        for host2 in trNet.hosts:
            if host1 != host2:
                startTime = time.time()
                host1.cmd("ping -c 1 %s"%(host2))
                endTime = time.time()
                print "RRT: "+str((endTime-startTime)*1000)+"ms"
    print "Testing bw between every pair of hosts:"
    print "Total host number: "+str(len(trNet.hosts))
    for i in range(len(trNet.hosts)):
        for j in range(i+1, len(trNet.hosts)):
            ha, hb = trNet.get('h'+str(i+1), 'h'+str(j+1))
            trNet.iperf((ha, hb))
    trNet.stop()
    os.system("sudo mn -c")
    
    print "Finished."

 
if __name__=='__main__':
    setLogLevel('info')
    perfTest()
