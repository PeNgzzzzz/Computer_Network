#!/usr/bin/python

"""Topology with 3 switches and 3 hosts
"""

from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel

class CSLRTopo( Topo ):

        def __init__( self ):
                "Create Topology"

                # Initialize topology
                Topo.__init__( self )

                # Add hosts
                Alice = self.addHost( 'Alice' )
                Bob = self.addHost( 'Bob' )
                Carol = self.addHost( 'Carol' )

                # Add switches
                R1 = self.addSwitch( 'R1', listenPort=6634 )
                R2 = self.addSwitch( 'R2', listenPort=6635 )
                R3 = self.addSwitch( 'R3', listenPort=6636 )

                # Add links between hosts and switches
                self.addLink( Alice, R1 ) # Alice-eth0 <-> R1-eth1
                self.addLink( Bob, R2 ) # Bob-eth0 <-> R2-eth1
                self.addLink( Carol, R3 ) # Carol-eth0 <-> R3-eth1

                # Add links between switches, with bandwidth 100Mbps
                self.addLink( R1, R2, bw=100 ) # R1-eth2 <-> R2-eth2, Bandwidth = 100Mbps
                self.addLink( R1, R3, bw=100 ) # R1-eth3 <-> R3-eth2, Bandwidth = 100Mbps
                self.addLink( R2, R3, bw=100 ) # R2-eth3 <-> R3-eth3, Bandwidth = 100Mbps

def run():
        "Create and configure network"
        topo = CSLRTopo()
        net = Mininet( topo=topo, link=TCLink, controller=None )

        # Set interface IP and MAC addresses for hosts
        Alice = net.get( 'Alice' )
        Alice.intf( 'Alice-eth0' ).setIP( '10.1.1.17', 24 )
        Alice.intf( 'Alice-eth0' ).setMAC( 'aa:aa:aa:aa:aa:aa' )

        Bob = net.get( 'Bob' )
        Bob.intf( 'Bob-eth0' ).setIP( '10.4.4.48', 24 )
        Bob.intf( 'Bob-eth0' ).setMAC( 'b0:b0:b0:b0:b0:b0' )

        Carol = net.get( 'Carol' )
        Carol.intf( 'Carol-eth0' ).setIP( '10.6.6.69', 24 )
        Carol.intf( 'Carol-eth0' ).setMAC( 'cc:cc:cc:cc:cc:cc' )

        # Set interface MAC address for switches (NOTE: IP
        # addresses are not assigned to switch interfaces)
        R1 = net.get( 'R1' )
        R1.intf( 'R1-eth1' ).setMAC( '0A:00:00:01:00:01' )
        R1.intf( 'R1-eth2' ).setMAC( '0A:00:0A:01:00:02' )
        R1.intf( 'R1-eth3' ).setMAC( '0A:00:0B:01:00:03' )

        R2 = net.get( 'R2' )
        R2.intf( 'R2-eth1' ).setMAC( '0A:00:01:01:00:01' )
        R2.intf( 'R2-eth2' ).setMAC( '0A:00:0A:FE:00:02' )
        R2.intf( 'R2-eth3' ).setMAC( '0A:00:0C:01:00:03' )

        R3 = net.get( 'R3' )
        R3.intf( 'R3-eth1' ).setMAC( '0A:00:02:01:00:01' )
        R3.intf( 'R3-eth2' ).setMAC( '0A:00:0B:FE:00:02' )
        R3.intf( 'R3-eth3' ).setMAC( '0A:00:0D:01:00:03' )

        net.start()

        # Add routing table entries for hosts (NOTE: The gateway
		# IPs 10.0.X.1 are not assigned to switch interfaces)
        Alice.cmd( 'route add default gw 10.1.1.14 dev Alice-eth0' )
        Bob.cmd( 'route add default gw 10.4.4.14 dev Bob-eth0' )
        Carol.cmd( 'route add default gw 10.6.6.46 dev Carol-eth0' )

        # Add arp cache entries for hosts
        Alice.cmd( 'arp -s 10.1.1.14 0A:00:00:01:00:01 -i Alice-eth0' )
        Bob.cmd( 'arp -s 10.4.4.14 0A:00:01:01:00:01 -i Bob-eth0' )
        Carol.cmd( 'arp -s 10.6.6.46 0A:00:02:01:00:01 -i Carol-eth0' )

        # Open Mininet Command Line Interface
        CLI(net)

        # Teardown and cleanup
        net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
