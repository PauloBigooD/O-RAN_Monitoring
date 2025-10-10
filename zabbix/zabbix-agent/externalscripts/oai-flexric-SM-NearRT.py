#!/usr/bin/env python3

import subprocess
import json
import re
import sys

def exit_with_empty_json():
    """Imprime um JSON com uma lista de dados vazia e encerra o script de forma limpa."""
    print(json.dumps({"data": []}, indent=4))
    sys.exit(0)

# --- Seção 1: Encontrar e Executar o xApp ---

cmd = "find /home /opt -type f -wholename '*/flexric/build/examples/xApp/c/helloworld/xapp_hw' 2>/dev/null"
try:
    file_path = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout.strip().split('\n')[0]
    if not file_path:
        exit_with_empty_json()
except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
    exit_with_empty_json()

try:
    result = subprocess.run(
        [file_path],
        capture_output=True,
        text=True,
        timeout=30
    )
    output_text = result.stdout
    if result.returncode != 0 or not output_text:
        exit_with_empty_json()
except (subprocess.TimeoutExpired, FileNotFoundError):
    exit_with_empty_json()

# --- Seção 2: Parsing dos Dados ---

data = {}
sm_mapping = {}

patterns = {
    "nearRT-RIC IP": r"nearRT-RIC IP Address\s*=\s*([\d\.]+)",
    "PORT": r"PORT\s*=\s*(\d+)",
    "SM_ID": r"SM ID\s*=\s*(\d+)\s+with def\s*=\s*([\w\-]+)",
    "node_info": r"E2 node (\d+) info: nb_id ([a-fA-F0-9]+), mcc (\d+), mnc (\d+), mnc_digit_len (\d+), ran_type ([\w_]+)",
    "ran_functions": r"E2 node (\d+) supported RAN function's IDs:, ([\d,\s]+)"
}

match_ip = re.search(patterns["nearRT-RIC IP"], output_text)
match_port = re.search(patterns["PORT"], output_text)
data["nearRT-RIC IP"] = match_ip.group(1) if match_ip else ""
data["PORT"] = int(match_port.group(1)) if match_port else 0

for sm_id, sm_def in re.findall(patterns["SM_ID"], output_text):
    sm_mapping[f"{{#NEAR_RT_RIC_SM_ID_{sm_id}}}"] = sm_def

main_info = {
    **sm_mapping,
    "{#NEAR_RT_RIC_IP}": data["nearRT-RIC IP"],
    "{#PORT}": data["PORT"]
}

# --- INÍCIO DA MUDANÇA IMPORTANTE ---
# Passo 1: Criar a "lista mestra" com todos os IDs de SMs que o RIC suporta.
all_ric_sm_ids = set()
for key in sm_mapping.keys():
    match = re.search(r'SM_ID_(\d+)', key)
    if match:
        all_ric_sm_ids.add(int(match.group(1)))
# --- FIM DA MUDANÇA IMPORTANTE ---

nodes_raw = {}
for match in re.finditer(patterns["node_info"], output_text):
    node_index, nb_id_hex, mcc, mnc, _, ran_type = match.groups()
    nodes_raw[node_index] = {
        "nb_id": int(nb_id_hex, 16),
        "mcc": int(mcc),
        "mnc": int(mnc),
        "ran_type": ran_type,
        "functions": []
    }

for match in re.finditer(patterns["ran_functions"], output_text):
    node_index, ran_ids = match.groups()
    if node_index in nodes_raw:
        ids = [int(rid.strip()) for rid in ran_ids.split(",") if rid.strip()]
        nodes_raw[node_index]["functions"] = ids

# --- Seção 3: Montagem do JSON Final ---

output = [main_info]

for node in nodes_raw.values():
    node_dict = {
        "{#GNB_ID}": node.get("nb_id", 0),
        "{#GNB_MCC}": node.get("mcc", 0),
        "{#GNB_MNC}": node.get("mnc", 0),
        "{#GNB_TYPE}": node.get("ran_type", "")
    }

    # --- INÍCIO DA MUDANÇA IMPORTANTE ---
    # Passo 2: Nova lógica para preencher os SMs da gNB.
    # Itera sobre a lista mestra de SMs do RIC, não sobre os SMs da gNB.
    gnb_supported_sm_ids = set(node.get("functions", []))
    
    for sm_id in all_ric_sm_ids:
        key = f"{{#GNB_SM_ID_{sm_id}}}"
        if sm_id in gnb_supported_sm_ids:
            # Se a gNB suporta este SM, o valor é o próprio ID.
            node_dict[key] = sm_id
        else:
            # Se a gNB NÃO suporta este SM, o valor é 0.
            node_dict[key] = 0
    # --- FIM DA MUDANÇA IMPORTANTE ---

    output.append(node_dict)

print(json.dumps({"data": output}, indent=4))
