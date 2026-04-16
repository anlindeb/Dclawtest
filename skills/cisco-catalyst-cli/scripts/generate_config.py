#!/usr/bin/env python3
"""
Generate common Cisco Catalyst config snippets.
Usage: python3 generate_config.py <template> [options]

Templates:
  access-port    Generate access port config
  trunk-port     Generate trunk port config
  vlan-batch     Generate multiple VLANs
  etherchannel   Generate LACP EtherChannel config
  initial-setup  Generate initial switch setup

Examples:
  python3 generate_config.py access-port --interface gi1/0/5 --vlan 10 --voice-vlan 20 --desc "User Desk"
  python3 generate_config.py trunk-port --interface gi1/0/24 --vlans 10,20,99
  python3 generate_config.py vlan-batch --vlans 10:USERS,20:VOICE,99:MGMT
  python3 generate_config.py etherchannel --channel 1 --interfaces gi1/0/1-2 --vlans 10,20,99
  python3 generate_config.py initial-setup --hostname SW-01 --domain example.com --mgmt-vlan 99 --mgmt-ip 10.1.99.1/24
"""

import argparse
import sys


def access_port(args):
    lines = [
        f"interface {args.interface}",
        f"  description {args.desc or 'Access Port'}",
        "  switchport mode access",
        f"  switchport access vlan {args.vlan}",
    ]
    if args.voice_vlan:
        lines.append(f"  switchport voice vlan {args.voice_vlan}")
    lines += [
        "  spanning-tree portfast",
        "  spanning-tree bpduguard enable",
        "  no shutdown",
    ]
    return "\n".join(lines)


def trunk_port(args):
    lines = [
        f"interface {args.interface}",
        f"  description {args.desc or 'Trunk Port'}",
        "  switchport trunk encapsulation dot1q",
        "  switchport mode trunk",
        f"  switchport trunk allowed vlan {args.vlans}",
    ]
    if args.native_vlan:
        lines.append(f"  switchport trunk native vlan {args.native_vlan}")
    lines.append("  no shutdown")
    return "\n".join(lines)


def vlan_batch(args):
    lines = []
    for entry in args.vlans.split(","):
        vid, name = entry.split(":")
        lines += [f"vlan {vid}", f"  name {name}"]
    return "\n".join(lines)


def etherchannel(args):
    lines = [
        f"interface range {args.interfaces}",
        f"  description Port-Channel {args.channel}",
        f"  channel-group {args.channel} mode active",
        "  no shutdown",
        "",
        f"interface port-channel {args.channel}",
        "  switchport trunk encapsulation dot1q",
        "  switchport mode trunk",
        f"  switchport trunk allowed vlan {args.vlans}",
    ]
    return "\n".join(lines)


def initial_setup(args):
    lines = [
        "configure terminal",
        f"hostname {args.hostname}",
        "no ip domain-lookup",
        f"ip domain-name {args.domain}",
        "",
        "! Enable SSH",
        "crypto key generate rsa modulus 2048",
        "ip ssh version 2",
        "username admin privilege 15 secret <CHANGE-ME>",
        "enable secret <CHANGE-ME>",
        "",
        "! VTY lines",
        "line vty 0 4",
        "  login local",
        "  transport input ssh",
        "",
        f"! Management VLAN {args.mgmt_vlan}",
        f"vlan {args.mgmt_vlan}",
        f"  name MGMT",
    ]
    if args.mgmt_ip:
        ip, mask = args.mgmt_ip.split("/")
        mask_bits = int(mask)
        subnet_mask = ".".join(
            str((0xFFFFFFFF << (32 - mask_bits)) >> (24 - 8 * i) & 0xFF)
            for i in range(4)
        )
        lines += [
            f"interface vlan {args.mgmt_vlan}",
            f"  ip address {ip} {subnet_mask}",
            "  no shutdown",
        ]
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate Cisco Catalyst config snippets")
    subparsers = parser.add_subparsers(dest="template", required=True)

    # access-port
    p = subparsers.add_parser("access-port")
    p.add_argument("--interface", required=True, help="Interface name (e.g. gi1/0/5)")
    p.add_argument("--vlan", required=True, type=int, help="Access VLAN ID")
    p.add_argument("--voice-vlan", type=int, help="Voice VLAN ID")
    p.add_argument("--desc", help="Interface description")

    # trunk-port
    p = subparsers.add_parser("trunk-port")
    p.add_argument("--interface", required=True)
    p.add_argument("--vlans", required=True, help="Allowed VLANs (comma-separated)")
    p.add_argument("--native-vlan", type=int, help="Native VLAN")
    p.add_argument("--desc", help="Interface description")

    # vlan-batch
    p = subparsers.add_parser("vlan-batch")
    p.add_argument("--vlans", required=True, help="VLANs as id:name,id:name (e.g. 10:USERS,20:VOICE)")

    # etherchannel
    p = subparsers.add_parser("etherchannel")
    p.add_argument("--channel", required=True, type=int, help="Port-channel number")
    p.add_argument("--interfaces", required=True, help="Interface range (e.g. gi1/0/1-2)")
    p.add_argument("--vlans", required=True, help="Allowed VLANs")

    # initial-setup
    p = subparsers.add_parser("initial-setup")
    p.add_argument("--hostname", required=True)
    p.add_argument("--domain", required=True)
    p.add_argument("--mgmt-vlan", required=True, type=int)
    p.add_argument("--mgmt-ip", help="Management IP in CIDR (e.g. 10.1.99.1/24)")

    args = parser.parse_args()

    generators = {
        "access-port": access_port,
        "trunk-port": trunk_port,
        "vlan-batch": vlan_batch,
        "etherchannel": etherchannel,
        "initial-setup": initial_setup,
    }

    print(generators[args.template](args))


if __name__ == "__main__":
    main()
