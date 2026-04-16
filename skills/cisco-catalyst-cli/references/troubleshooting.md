# Cisco Catalyst Troubleshooting Workflows

## Table of Contents
1. [Interface Won't Come Up](#interface-wont-come-up)
2. [VLAN Connectivity Issues](#vlan-connectivity-issues)
3. [Spanning Tree Problems](#spanning-tree-problems)
4. [EtherChannel Won't Form](#etherchannel-wont-form)
5. [Intermittent Connectivity](#intermittent-connectivity)
6. [High CPU](#high-cpu)
7. [Cannot SSH/Telnet](#cannot-sshtelnet)

## Interface Won't Come Up

```
1. show interfaces gi1/0/1 status
   - Is it "notconnect"? Check physical layer (cable, SFP, far end)
   - Is it "err-disable"? See below
   - Is it "disabled"? Interface is shut down

2. show interfaces gi1/0/1
   - Look at line protocol (up/down)
   - Check for errors: CRC, input/output errors, collisions

3. show interfaces gi1/0/1 transceiver (fiber)
   - Check Tx/Rx power levels

4. Err-disable recovery:
   show errdisable recovery
   show interfaces status err-disabled
   errdisable recovery cause <reason>
   errdisable recovery interval 300
   ! Or manually re-enable:
   interface gi1/0/1
     shutdown
     no shutdown
```

## VLAN Connectivity Issues

```
1. show vlan brief
   - Is the port in the right VLAN?
   - Does the VLAN exist?

2. show interfaces trunk
   - Is the trunk allowing the VLAN?
   - Native VLAN mismatch? (show cdp neighbors detail)

3. show spanning-tree vlan <id>
   - Is the VLAN forwarding on the right ports?
   - Any blocked ports?

4. show ip interface brief
   - Is the SVI up? (interface vlan X needs "no shutdown" + active ports in VLAN)
```

## Spanning Tree Problems

```
1. show spanning-tree detail
   - Identify root bridge — is it the expected switch?
   - Check for unexpected topology changes

2. show spanning-tree blockedports
   - Which ports are blocking? Expected?

3. show spanning-tree inconsistentports
   - Port type inconsistencies (edge vs network)

4. Common fixes:
   spanning-tree vlan <id> root primary    ! Force root
   spanning-tree portfast                   ! Access ports only
   spanning-tree bpduguard enable           ! Protect against loops
   spanning-tree guard root                 ! Prevent unwanted roots
```

## EtherChannel Won't Form

```
1. show etherchannel summary
   - Are members in correct state? (I = standalone, P = bundled)
   - Which protocol? LACP (Su) vs PAgP (au)

2. show etherchannel <id> detail
   - Check partner info — both sides must agree on:
     * Mode (active/passive vs desirable/auto)
     * Allowed VLANs
     * Trunk encapsulation
     * Speed/duplex

3. Common issues:
   - One side active, other side passive → works (both active preferred)
   - One side on, other side off → won't form
   - Mismatched trunk config → suspended
   - More than 8 active members → extras are standby (LACP)
   - Different speed/duplex → won't bundle

4. Check LACP negotiation:
   show lacp neighbor
   show lacp sys-id
```

## Intermittent Connectivity

```
1. show mac address-table | include <mac>
   - Is the MAC flapping between ports?

2. show logging | include MACFLAP
   - MAC flapping = loop or misconfigured redundant path

3. show interfaces <id> counters errors
   - CRC errors = bad cable or duplex mismatch
   - Collisions = half-duplex negotiation issue

4. Duplex mismatch check:
   show interfaces <id> | include Duplex
   - Never hardcode one side and auto-negotiate the other
   - Best practice: auto-negotiate both sides, or hardcode both
```

## High CPU

```
1. show processes cpu sorted
   - Identify the top CPU-consuming process
   - Common culprits:
     * Hulc LED = normal (hardware monitoring)
     * IP Input = process-switched traffic (CEF broken?)
     * Spanning Tree = topology changes
     * ARP = ARP storm

2. show processes cpu history
   - Is it sustained or spikes?

3. show cef not-cef-switched
   - Traffic not hardware-forwarded

4. Quick fixes:
   ip cef                          ! Ensure CEF enabled
   no ip redirects                 ! Reduce ICMP processing
   spanning-tree portfast          ! Reduce STP processing on edge
```

## Cannot SSH/Telnet

```
1. show ip ssh
   - Is SSH enabled? Version 2?

2. show line vty 0 4
   - Transport input configured?
   - Login method? (local, AAA, none)

3. show running-config | section line vty
   - Verify transport input ssh (or telnet)
   - Verify login local or login authentication

4. show access-lists
   - Is there an ACL blocking access?

5. Check crypto keys:
   show crypto key mypubkey rsa
   ! If missing:
   crypto key generate rsa modulus 2048

6. Ping test:
   ping <switch-ip> from source
```
