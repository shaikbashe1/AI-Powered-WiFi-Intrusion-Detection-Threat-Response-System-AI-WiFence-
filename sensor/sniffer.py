# sensor/sniffer.py
"""
Lightweight packet sniffer that saves packet metadata to captures.jsonl.
Run on a device that can capture traffic you own. Requires root for
monitor-mode captures. Alternative: capture on gateway (eth0) with tcpdump.
"""

import json
import time
import argparse
from scapy.all import sniff
from scapy.layers.dot11 import Dot11
from scapy.layers.inet import IP, TCP, UDP, ICMP

OUTFILE = "captures.jsonl"

def pkt_to_record(pkt):
    rec = {
        "ts": time.time(),
        "len": len(pkt)
    }
    try:
        if pkt.haslayer(Dot11):
            rec["mac_src"] = pkt.addr2
            rec["mac_dst"] = pkt.addr1
            # Dot11 subtype can hint deauth, probe, etc.
            rec["dot11_subtype"] = int(pkt.subtype)
    except Exception:
        pass

    try:
        if pkt.haslayer(IP):
            ip = pkt.getlayer(IP)
            rec["ip_src"] = ip.src
            rec["ip_dst"] = ip.dst
            rec["proto"] = int(ip.proto)
    except Exception:
        pass

    try:
        if pkt.haslayer(TCP):
            tcp = pkt.getlayer(TCP)
            rec["dst_port"] = int(tcp.dport)
            rec["src_port"] = int(tcp.sport)
        elif pkt.haslayer(UDP):
            udp = pkt.getlayer(UDP)
            rec["dst_port"] = int(udp.dport)
            rec["src_port"] = int(udp.sport)
        elif pkt.haslayer(ICMP):
            rec["icmp"] = True
    except Exception:
        pass

    return rec

def write_record(rec, outfile=OUTFILE):
    with open(outfile, "a") as f:
        f.write(json.dumps(rec) + "\n")

def handle_packet(pkt):
    rec = pkt_to_record(pkt)
    write_record(rec)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iface", default="wlan0mon", help="Interface to sniff (monitor/gateway)")
    parser.add_argument("--outfile", default=OUTFILE)
    args = parser.parse_args()

    global OUTFILE
    OUTFILE = args.outfile
    print(f"[+] Sniffing on {args.iface}, writing to {OUTFILE}")
    sniff(iface=args.iface, prn=handle_packet, store=False)

if __name__ == "__main__":
    main()
