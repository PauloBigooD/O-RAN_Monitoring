#!/usr/bin/env python3
import sys
import argparse
import os
import re
import redis
import binascii
from lib.xAppBase import xAppBase

DB_HOST = os.environ.get("DBAAS_SERVICE_HOST", "10.0.2.12")
DB_PORT = os.environ.get("DBAAS_SERVICE_PORT", "6379")

class DynamicDiscoveryXappV9(xAppBase):
    def __init__(self, config, http_server_port, rmr_port):
        super(DynamicDiscoveryXappV9, self).__init__(config, http_server_port, rmr_port)
        
        self.found_oids = []
        self.kpm_metrics = set()
        self.kpm_styles = set()
        
        # RC Data
        self.rc_actions_found = set()
        self.rc_params_found = set()
        
        self.e2ap_version = "Unknown"

        # --- Dicionários de Busca (RC) ---
        self.RC_ACTIONS_DICT = [
            "Slice-level PRB quota", "Radio Resource Allocation Control",
            "QoS Flow Mapping", "DRB Termination Control"
        ]
        self.RC_PARAMS_DICT = [
            "RRM Policy Ratio List", "RRM Policy Ratio Group", "RRM Policy Member", "RRM Policy",
            "PLMN Identity", "SST", "SD", "S-NSSAI",
            "Min PRB Policy Ratio", "Max PRB Policy Ratio", "Dedicated PRB Policy Ratio",
            "FiveQI", "QFI"
        ]

        # --- MAPA DE OIDs: OFICIAL vs EXPERIMENTAL ---
        self.OID_MAP = {
            # --- OFFICIAL O-RAN WG3 SPECIFICATIONS ---
            "1.3.6.1.4.1.53148.1.2.2":   "E2SM-KPM (Standard)",       # Covers v1, v2, v3
            "1.3.6.1.4.1.53148.1.1.2.3": "E2SM-RC (Standard)",        # RAN Control
            "1.3.6.1.4.1.53148.1.2.1":   "E2SM-NI (Standard)",        # Network Interface
            "1.3.6.1.4.1.53148.1.2.4":   "E2SM-CCC (Standard)",       # Cell Config & Control
            
            # --- FOUND IN O-RAN SPECS (USER REQUEST) ---
            "1.3.6.1.4.1.53148.1.1.2":   "E2SM-LLC (Standard - Low Level Control)", 

            # --- O-RAN SOFTWARE COMMUNITY (OSC) / FLEXRIC IMPLEMENTATIONS ---
            # Estes não são specs oficiais WG3, mas modelos de implementação
            "1.3.6.1.4.1.53148.1.2.3":   "E2SM-MHO (Experimental/OSC - Handover)",
            "1.3.6.1.4.1.53148.1.2.5":   "E2SM-PCI (Experimental/OSC - PCI Opt)",
        }

    def get_redis_data(self, node_id):
        print(f"Connecting to SDL (Redis) at {DB_HOST}:{DB_PORT}...")
        try:
            r = redis.Redis(host=DB_HOST, port=int(DB_PORT), db=0, decode_responses=False)
            keys = r.keys(f"*{node_id}*")
            best_blob = b""
            for k in keys:
                if b"meta" in k or len(r.get(k)) < 100: continue
                val = r.get(k)
                if len(val) > len(best_blob): best_blob = val
            
            if best_blob:
                print(f"Loaded Raw Data: {len(best_blob)} bytes.")
                return best_blob
            return None
        except Exception as e:
            print(f"Redis Error: {e}")
            return None

    def sanitize_binary_to_text(self, data):
        text_out = ""
        for byte in data:
            char = chr(byte)
            if char.isprintable() and (char.isalnum() or char in ".-_ :"):
                text_out += char
            else:
                text_out += " "
        return re.sub(' +', ' ', text_out)

    def analyze_payload(self, raw_data):
        print("Scanning payload (Compliance Check)...")
        
        potential_blobs = [raw_data]
        try:
            raw_str_view = raw_data.decode('latin-1')
            hex_matches = re.findall(r'[0-9A-Fa-f]{100,}', raw_str_view)
            for h in hex_matches:
                try:
                    potential_blobs.append(binascii.unhexlify(h))
                except: pass
        except: pass

        full_text_corpus = ""
        for blob in potential_blobs:
            full_text_corpus += " " + self.sanitize_binary_to_text(blob)

        corpus_lower = full_text_corpus.lower()

        # E2AP Check
        if "e2ap_v2" in corpus_lower or "e2ap v2" in corpus_lower:
            self.e2ap_version = "E2AP v2.0 (O-RAN.WG3.E2AP-v02.00)"
        elif "e2ap_v1" in corpus_lower:
            self.e2ap_version = "E2AP v1.1 (O-RAN.WG3.E2AP-v01.01)"
        else:
            if "1.3.6.1.4.1.53148" in full_text_corpus:
                self.e2ap_version = "E2AP v2.0 (Inferred from E2SM OIDs)"

        # OID Extraction
        oids = re.findall(r'1\.3\.6\.1\.4\.1\.[0-9.]+', full_text_corpus)
        for o in oids:
            o_clean = o.rstrip('.')
            if len(o_clean) > 15 and o_clean not in self.found_oids:
                self.found_oids.append(o_clean)

        # Metrics & Actions Extraction
        metrics_candidates = re.findall(r'(DRB\.[a-zA-Z0-9]+|RRU\.[a-zA-Z0-9]+|RACH\.[a-zA-Z0-9]+|RSRP|RSRQ|CQI|SINR)', full_text_corpus)
        for m in metrics_candidates: self.kpm_metrics.add(m)

        if "node measurement" in corpus_lower: self.kpm_styles.add(1)
        if "single ue" in corpus_lower or "per ue" in corpus_lower: self.kpm_styles.add(2)
        if "condition" in corpus_lower: self.kpm_styles.add(3)
        if "common" in corpus_lower: self.kpm_styles.add(4)
        if "multiple ues" in corpus_lower: self.kpm_styles.add(5)
        
        ue_metrics = [m for m in self.kpm_metrics if "UE" in m or "RSRP" in m or "CQI" in m]
        if len(ue_metrics) > 0 and 2 not in self.kpm_styles: self.kpm_styles.add(2)

        for action in self.RC_ACTIONS_DICT:
            if action.lower() in corpus_lower: self.rc_actions_found.add(action)
        
        for param in self.RC_PARAMS_DICT:
            if len(param) <= 3:
                if f" {param.lower()} " in corpus_lower: self.rc_params_found.add(param)
            else:
                if param.lower() in corpus_lower: self.rc_params_found.add(param)

    def generate_report(self, node_id):
        KPM_STYLE_NAMES = {
            1: "E2 Node Measurement (Periodic)",
            2: "E2 Node Measurement (Single UE)",
            3: "Condition-based Measurement (UE-level)",
            4: "Common Condition-based",
            5: "Multiple UEs Measurement"
        }
        
        print("\n" + "="*60)
        print(f"[NODE 0] Dynamic Discovery Report (v9 - Compliance Audit)")
        print("="*60)
        print(f"    Target: {node_id}")
        
        print("    [+] Protocol Versions Detected:")
        print(f"        -> Transport: {self.e2ap_version}")
        
        print("\n    [+] Service Models (E2SM) Analysis:")
        
        if not self.found_oids:
            print("        (No OIDs found)")
        
        for oid in self.found_oids:
            name = "Unknown / Vendor Specific"
            # Match Logic
            for map_oid, map_name in self.OID_MAP.items():
                if map_oid in oid:
                    name = map_name
                    break
            
            # Formatação baseada no tipo (Standard vs Experimental)
            prefix = "" if "Standard" in name else ""
            if name == "Unknown / Vendor Specific": prefix = ""
            
            print(f"        -> {prefix} {name}")
            print(f"           OID: {oid}")

        # --- KPM SECTION ---
        if self.kpm_metrics or self.kpm_styles:
            print("\n    [+] DEEP DIVE: E2SM-KPM Capabilities")
            
            rru_metrics = sorted([m for m in self.kpm_metrics if "RRU" in m])
            ue_metrics  = sorted([m for m in self.kpm_metrics if m not in rru_metrics])
            
            for s in sorted(list(self.kpm_styles)):
                s_name = KPM_STYLE_NAMES.get(s, "Unknown Style")
                print(f"\n        Style Type: {s} | Name: {s_name}")
                print("          [Measurements List]:")
                
                current_list = []
                if s == 1: current_list = rru_metrics
                else: current_list = ue_metrics
                
                if current_list:
                    for m in current_list: print(f"           - {m}")
                else:
                    print("           (No specific metrics detected for this category)")

        # --- RC SECTION ---
        if self.rc_actions_found or self.rc_params_found:
            print("\n    [+] DEEP DIVE: E2SM-RC Capabilities")
            is_rrm = any("PRB" in a or "Slice" in a for a in self.rc_actions_found)
            
            if is_rrm:
                print("        -> Control Style: 1 (RRM / Resource Allocation)")
                print("           (Note: Mapped to Style 1 by Vendor)")
            else:
                print("        -> Control Style: Generic")

            if self.rc_actions_found:
                print("          [Supported Actions]:")
                for action in sorted(list(self.rc_actions_found)):
                     print(f"           > {action}")
            
            if self.rc_params_found:
                print("          [Control Parameters]:")
                for param in sorted(list(self.rc_params_found)):
                     print(f"           >> {param}")

        print("\n" + "-"*60)
        print("Discovery finished.")
        sys.exit(0)

    def execute_audit(self, node_id):
        raw_data = self.get_redis_data(node_id)
        if raw_data:
            self.analyze_payload(raw_data)
            self.generate_report(node_id)
        else:
            print("No data found.")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nodeid", type=str, required=True, help="E2 Node ID")
    args = parser.parse_args()
    
    xapp = DynamicDiscoveryXappV9('', 8090, 4560)
    xapp.execute_audit(args.nodeid)

if __name__ == '__main__':
    main()
