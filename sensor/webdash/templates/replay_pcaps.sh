#!/usr/bin/env bash
# demo/replay_pcaps.sh
# Replay pcap onto interface - only in an isolated lab network you control.
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <interface> <pcap-file>"
  exit 1
fi
IFACE="$1"
PCAP="$2"
echo "Replaying $PCAP on $IFACE (ensure this is a test network)"
tcpreplay --intf1="$IFACE" "$PCAP"
