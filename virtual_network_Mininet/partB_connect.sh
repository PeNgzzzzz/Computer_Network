#!/usr/bin/env bash

# Sets bridge R1 to use OpenFlow 1.3
ovs-vsctl set bridge R1 protocols=OpenFlow13 

# Sets bridge R2 to use OpenFlow 1.3
ovs-vsctl set bridge R2 protocols=OpenFlow13 

# Sets bridge R3 to use OpenFlow 1.3
ovs-vsctl set bridge R3 protocols=OpenFlow13 

# Print the protocols that each switch supports
for switch in R1 R2 R3;
do
    protos=$(ovs-vsctl get bridge $switch protocols)
    echo "Switch $switch supports $protos"
done

# Avoid having to write "-O OpenFlow13" before all of your ovs-ofctl commands.
ofctl='ovs-ofctl -O OpenFlow13'

# (Alice <-> Bob)
# OVS rules for R1
$ofctl add-flow R1 \
    ip,nw_src=10.1.1.17,nw_dst=10.4.4.48,actions=mod_dl_src:0A:00:0A:01:00:02,mod_dl_dst:0A:00:0A:FE:00:02,output=2 

$ofctl add-flow R1 \
    ip,nw_src=10.4.4.48,nw_dst=10.1.1.17,actions=mod_dl_src:0A:00:00:01:00:01,mod_dl_dst:aa:aa:aa:aa:aa:aa,output=1 

# OVS rules for R2
$ofctl add-flow R2 \
    ip,nw_src=10.1.1.17,nw_dst=10.4.4.48,actions=mod_dl_src:0A:00:01:01:00:01,mod_dl_dst:b0:b0:b0:b0:b0:b0,output=1 

$ofctl add-flow R2 \
    ip,nw_src=10.4.4.48,nw_dst=10.1.1.17,actions=mod_dl_src:0A:00:0A:FE:00:02,mod_dl_dst:0A:00:0A:01:00:02,output=2 


# (Bob <-> Carol)
# OVS rules for R2
$ofctl add-flow R2 \
    ip,nw_src=10.4.4.48,nw_dst=10.6.6.69,actions=mod_dl_src:0A:00:0C:01:00:03,mod_dl_dst:0A:00:0D:01:00:03,output=3

$ofctl add-flow R2 \
    ip,nw_src=10.6.6.69,nw_dst=10.4.4.48,actions=mod_dl_src:0A:00:01:01:00:01,mod_dl_dst:b0:b0:b0:b0:b0:b0,output=1 

# OVS rules for R3
$ofctl add-flow R3 \
    ip,nw_src=10.4.4.48,nw_dst=10.6.6.69,actions=mod_dl_src:0A:00:02:01:00:01,mod_dl_dst:cc:cc:cc:cc:cc:cc,output=1

$ofctl add-flow R3 \
    ip,nw_src=10.6.6.69,nw_dst=10.4.4.48,actions=mod_dl_src:0A:00:0D:01:00:03,mod_dl_dst:0A:00:0C:01:00:03,output=3  


# Print the flows installed in each switch
for switch in R1 R2 R3; 
do
    echo "Flows installed in $switch:"
    $ofctl dump-flows $switch
    echo ""
done