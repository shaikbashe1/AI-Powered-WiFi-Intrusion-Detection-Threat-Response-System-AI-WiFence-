# processor/feature_builder.py
"""
Read captures.jsonl and build per-device features using a sliding window.
Outputs a pandas DataFrame suitable for model training/inference.
"""

import pandas as pd
import time
import json

def load_recent_events(jsonl_path="captures.jsonl", window_seconds=60):
    """
    Load file and return rows within window_seconds from now.
    If file is large, consider rotating or truncating periodically.
    """
    try:
        df = pd.read_json(jsonl_path, lines=True)
    except ValueError:
        # no data yet
        return pd.DataFrame()
    cutoff = time.time() - window_seconds
    df = df[df["ts"] >= cutoff]
    # normalize columns
    if 'mac_src' not in df.columns:
        df['mac_src'] = None
    if 'dst_port' not in df.columns:
        df['dst_port'] = None
    return df

def build_device_features(df):
    """
    For each mac_src build features:
      - pkts, bytes, avg_len, std_len
      - unique_dst_ips, unique_dst_ports
      - tcp_udp_ratio (approx), arp_count (if present)
    """
    if df.empty:
        return pd.DataFrame()
    # make sure numeric
    df['len'] = df['len'].fillna(0).astype(float)
    feature_rows = []
    for mac, g in df.groupby('mac_src'):
        if pd.isna(mac):
            continue
        pkts = len(g)
        total_bytes = float(g['len'].sum())
        avg_len = float(g['len'].mean()) if pkts > 0 else 0.0
        std_len = float(g['len'].std()) if pkts > 1 else 0.0
        unique_dst_ips = int(g['ip_dst'].nunique()) if 'ip_dst' in g else 0
        unique_dst_ports = int(g['dst_port'].nunique()) if 'dst_port' in g else 0
        tcp_count = int((g['proto'] == 6).sum()) if 'proto' in g else 0
        udp_count = int((g['proto'] == 17).sum()) if 'proto' in g else 0
        icmp_count = int(g.get('icmp', 0).sum()) if 'icmp' in g else 0
        # proxy deauth by dot11_subtype 12/8 etc. (depends on capture)
        deauth_count = int((g.get('dot11_subtype', 0) == 12).sum()) if 'dot11_subtype' in g else 0

        row = {
            "mac": mac,
            "pkts": pkts,
            "bytes": total_bytes,
            "avg_len": avg_len,
            "std_len": std_len,
            "unique_dst_ips": unique_dst_ips,
            "unique_dst_ports": unique_dst_ports,
            "tcp_count": tcp_count,
            "udp_count": udp_count,
            "icmp_count": icmp_count,
            "deauth_count": deauth_count,
        }
        feature_rows.append(row)
    feat_df = pd.DataFrame(feature_rows).fillna(0)
    return feat_df

if __name__ == "__main__":
    df = load_recent_events(window_seconds=60)
    feats = build_device_features(df)
    print(feats.head())
