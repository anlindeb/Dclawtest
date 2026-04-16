---
name: cisco-catalyst-cli
description: "Configure, troubleshoot, and manage Cisco Catalyst switches via CLI. Use when working with Cisco IOS/IOS-XE commands, switch configuration, VLANs, STP, port security, EtherChannel, ACLs, routing, or any Catalyst switch CLI task. Triggers on: Cisco switch config, show commands, interface configuration, trunk/access port setup, VLAN management, Spanning Tree, ACLs, DHCP snooping, port-channel, stackwise, or any Catalyst CLI scenario."
---

# Cisco Catalyst CLI

Configure and manage Cisco Catalyst switches running IOS or IOS-XE.

## Quick Reference

| Mode | Prompt | Enter | Exit |
|------|--------|-------|------|
| User EXEC | `Switch>` | (default) | `logout` |
| Privileged EXEC | `Switch#` | `enable` | `disable` |
| Global Config | `Switch(config)#` | `configure terminal` | `exit` / `end` |
| Interface Config | `Switch(config-if)#` | `interface gi1/0/1` | `exit` / `end` |
| Line Config | `Switch(config-line)#` | `line vty 0 4` | `exit` / `end` |
| VLAN Config | `Switch(config-vlan)#` | `vlan 10` | `exit` / `end` |

## Common Workflows

### 1. Initial Switch Setup

```
enable
configure terminal
hostname SW-ACCESS-01
no ip domain-lookup
enable secret <secret>
username admin privilege 15 secret <password>
line vty 0 4
  login local
  transport input ssh
ip domain-name example.com
crypto key generate rsa modulus 2048
ip ssh version 2
```

### 2. VLAN Configuration

```
vlan 10
  name USERS
vlan 20
  name VOICE
vlan 99
  name MANAGEMENT
exit

! SVI for management
interface vlan 99
  ip address 10.1.99.1 255.255.255.0
  no shutdown
```

### 3. Access Port (Data + Voice)

```
interface gi1/0/5
  description User Workstation
  switchport mode access
  switchport access vlan 10
  switchport voice vlan 20
  spanning-tree portfast
  spanning-tree bpduguard enable
  no shutdown
```

### 4. Trunk Port

```
interface gi1/0/24
  description Uplink to Core
  switchport trunk encapsulation dot1q
  switchport mode trunk
  switchport trunk allowed vlan 10,20,99
  no shutdown
```

### 5. EtherChannel (LACP)

```
interface range gi1/0/1-2
  description Port-Channel to Distribution
  channel-group 1 mode active
  no shutdown

interface port-channel 1
  switchport trunk encapsulation dot1q
  switchport mode trunk
  switchport trunk allowed vlan 10,20,99
```

### 6. Port Security

```
interface gi1/0/5
  switchport port-security
  switchport port-security maximum 2
  switchport port-security mac-address sticky
  switchport port-security violation restrict
```

### 7. Spanning Tree

```
! Root bridge for VLAN 10
spanning-tree vlan 10 root primary
spanning-tree vlan 20 root secondary

! Rapid PVST+ (recommended)
spanning-tree mode rapid-pvst

! Verify
show spanning-tree vlan 10
```

### 8. ACLs

```
! Extended named ACL
ip access-list extended BLOCK_GUEST_INTERNET
  deny ip 10.1.30.0 0.0.0.255 any
  permit ip any any

! Apply to interface
interface gi1/0/10
  ip access-group BLOCK_GUEST_INTERNET in
```

### 9. DHCP Snooping

```
ip dhcp snooping
ip dhcp snooping vlan 10,20
no ip dhcp snooping information option

! Trust on uplinks
interface gi1/0/24
  ip dhcp snooping trust
```

### 10. Save & Verify

```
! Save config
copy running-config startup-config
! or
write memory

! Key show commands
show running-config
show ip interface brief
show interfaces status
show vlan brief
show spanning-tree
show etherchannel summary
show mac address-table
show cdp neighbors
show logging
show version
```

## Troubleshooting Commands

| Issue | Command |
|-------|---------|
| Interface down | `show interfaces gi1/0/1 status` / `show interfaces gi1/0/1` |
| VLAN mismatch | `show interfaces trunk` / `show vlan brief` |
| STP issues | `show spanning-tree detail` / `show spanning-tree blockedports` |
| MAC flapping | `show mac address-table` / `show logging \| include MACFLAP` |
| EtherChannel down | `show etherchannel summary` / `show etherchannel 1 detail` |
| High CPU | `show processes cpu sorted` |
| Memory | `show processes memory` |
| ARP issues | `show ip arp` / `show ip arp inspection` |
| Port security violation | `show port-security interface gi1/0/5` |
| CDP/LLDP neighbors | `show cdp neighbors detail` / `show lldp neighbors detail` |

## StackWise (Catalyst 9200/9300/9500)

```
! Check stack status
show switch
show stack-ports

! Priority (higher = preferred master)
switch 1 priority 15
switch 2 priority 10

! Provision a new member
switch 3 provision ws-c9300-24t

! Reload single member
reload slot 3
```

## IOS-XE Differences

IOS-XE uses a Linux-based shell underneath. Key differences:

- **Config mode**: Same CLI, but supports `show running-config` with section filtering:
  ```
  show running-config | section interface
  show running-config | section spanning-tree
  ```
- **Guest shell**: Available on newer platforms for Linux tools
  ```
  guestshell
  ```
- **Netconf/RESTCONF**: IOS-XE supports programmable interfaces alongside CLI
- **Software install** (IOS-XE):
  ```
  install add file flash:cat9k_iosxe.17.12.01.SPA.bin activate commit
  ```

## References

For detailed command references and platform-specific syntax, see:
- **references/ios-xe-quick-ref.md** — IOS-XE command cheat sheet
- **references/troubleshooting.md** — systematic troubleshooting workflows
