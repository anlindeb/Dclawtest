# IOS-XE Quick Reference

## Table of Contents
1. [Interface Types & Naming](#interface-types--naming)
2. [Config Replacement vs Merge](#config-replacement-vs-merge)
3. [Software Management](#software-management)
4. [programmability](#programmability)
5. [Debugging](#debugging)
6. [Useful show Commands](#useful-show-commands)

## Interface Types & Naming

| Platform | Copper | Fiber/Uplink | Port-Channel |
|----------|--------|-------------|-------------|
| C9200 | `Gi1/0/1` | `Te1/0/1` | `Po1` |
| C9300 | `Gi1/0/1` | `Te1/0/1` / `Twe1/0/1` | `Po1` |
| C9500 | `Te1/0/1` | `Hu1/0/1` / `Fo1/0/1` | `Po1` |

- Gi = GigabitEthernet (1 Gbps)
- Te = TenGigabitEthernet (10 Gbps)
- Twe = TwentyFiveGigE (25 Gbps)
- Hu = HundredGigE (100 Gbps)
- Fo = FortyGigE (40 Gbps)

## Config Replacement vs Merge

IOS-XE supports config replace (rollback) natively:

```
! Save current config as baseline
copy running-config flash:baseline.cfg

! Replace entire config (atomic rollback)
configure replace flash:baseline.cfg

! Rollback with timer (auto-revert if disconnected)
configure replace flash:baseline.cfg timer 10
```

## Software Management

```
! Check current version
show version

! Install workflow (IOS-XE 16.x+)
install add file flash:cat9k_iosxe.17.12.01.SPA.bin activate commit

! One-shot (add + activate + commit)
install add file usb0:cat9k_iosxe.bin activate commit

! Rollback
install rollback to committed
install rollback to base

! Check install state
install summary
install active
install committed
```

## Programmability

```
! Enable NETCONF
netconf-yang

! Enable RESTCONF
ip http server
ip http secure-server
restconf

! Enable gNMI/gRPC
grpc port 57400

! Verify
show netconf-yang status
show restconf status
```

## Debugging

```
! Interface debugging
debug interfaces
debug etherchannel

! STP debugging
debug spanning-tree events

! DHCP snooping
debug ip dhcp snooping packet

! ARP debugging
debug ip arp

! Always disable after use
undebug all
```

## Useful show Commands

```
! Config diff
show running-config diff

! Interface counters (detailed)
show interfaces gi1/0/1 counters

! QoS
show policy-map interface

! Netflow
show flow monitor

! Environment
show environment
show environment temperature
show environment power

! Memory/CPU history
show processes cpu history
show processes memory history

! Boot variables
show boot

! License
show license summary
show license usage
```
