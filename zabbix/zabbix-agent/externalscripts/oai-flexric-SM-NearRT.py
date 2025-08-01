#!/usr/bin/env python3

import subprocess
import json
import re

# Encontrar o executável do xApp
cmd = "find / -type f -wholename '/home/ric-bigood/Documents/flexric/flexric/build/examples/xApp/c/helloworld/xapp_hw' 2>/dev/null"
try:
    file_path = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
    if not file_path:
        #print("Arquivo não encontrado.")
        exit(1)
except Exception as e:
    #print("Erro ao localizar o arquivo:", e)
    exit(1)

# Executar o xApp
try:
    result = subprocess.run(
        [file_path],
        capture_output=True,
        text=True,
        timeout=30
    )
    output_lines = result.stdout.splitlines()
except subprocess.TimeoutExpired:
    #print("O script demorou muito para responder e foi interrompido.")
    exit(1)
except Exception as e:
    #print("Erro ao executar o script:", e)
    exit(1)

output_text = "\n".join(output_lines)

# Expressões regulares
patterns = {
    "nearRT-RIC IP": r"nearRT-RIC IP Address\s*=\s*([\d\.]+)",
    "PORT": r"PORT\s*=\s*(\d+)",
    "SM_ID": r"SM ID\s*=\s*(\d+)",
    "with def": r"with def\s*=\s*([\w\-]+)",
    "node_info": r"E2 node (\d+) info: nb_id (\d+), mcc (\d+), mnc (\d+), mnc_digit_len (\d+), ran_type ([\w_]+)",
    "ran_functions": r"E2 node (\d+) supported RAN function's IDs:, ([\d,\s]+)"
}

# Coleta de IP e Porta
data = {}
sm_mapping = {}

for key, pattern in patterns.items():
    matches = re.findall(pattern, output_text)
    if key == "SM_ID":
        sm_ids = matches
    elif key == "with def":
        sm_defs = matches
    elif matches and key not in ["node_info", "ran_functions"]:
        data[key] = matches[0]

# Mapeamento de SM_IDs
if 'sm_ids' in locals() and 'sm_defs' in locals() and len(sm_ids) == len(sm_defs):
    for sm_id, sm_def in zip(sm_ids, sm_defs):
        sm_mapping[f"{{#NEAR_RT_RIC_SM_ID_{sm_id}}}"] = sm_def

# Dados principais (IP, PORT)
main_info = {
    **sm_mapping,
    "{#NEAR_RT_RIC_IP}": data.get("nearRT-RIC IP", ""),
    "{#PORT}": data.get("PORT", "")
}

# Coleta dos nós E2
nodes_raw = {}
for match in re.finditer(patterns["node_info"], output_text):
    node_index, nb_id, mcc, mnc, _, ran_type = match.groups()
    nodes_raw[node_index] = {
        "nb_id": int(nb_id),
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

# Montagem do JSON final
output = [main_info]

for node in nodes_raw.values():
    node_dict = {
        "{#GNB_ID}": node["nb_id"],
        "{#GNB_MCC}": node["mcc"],
        "{#GNB_MNC}": node["mnc"],
        "{#GNB_TYPE}": node["ran_type"]
    }
    for sm_id in node["functions"]:
        node_dict[f"{{#GNB_SM_ID_{sm_id}}}"] = sm_id
    output.append(node_dict)

print(json.dumps({"data": output}, indent=4))
