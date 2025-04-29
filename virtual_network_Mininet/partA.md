# Part A

### $ofctl add-flow s0 in_port=1,ip,nw_src=10.0.0.2,nw_dst=10.0.1.2,actions=mod_dl_src:0A:00:0A:01:00:02,mod_dl_dst:0A:00:0A:FE:00:02,output=2 
1. in_port=1: Matches packets entering s0 on port 1.
2. ip: Matches IP packets.
3. nw_src=10.0.0.2: Matches packets with source IP address 10.0.0.2.
4. nw_dst=10.0.1.2: Matches packets destined for IP address 10.0.1.2.
5. actions=: Specifies the actions to perform on matched packets.
6. mod_dl_src:0A:00:0A:01:00:02: Modifies the source MAC address to 0A:00:0A:01:00:02.
7. mod_dl_dst:0A:00:0A:FE:00:02: Modifies the destination MAC address to 0A:00:0A:FE:00:02.
8. output=2: Forwards the modified packet out of port 2.