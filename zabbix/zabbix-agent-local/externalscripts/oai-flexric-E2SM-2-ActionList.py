#!/usr/bin/env python3

import subprocess
import json
import re
import sys

def find_xapp():
    """Localiza o executável do xApp"""
    try:
        cmd = "find / -type f -wholename '*/build/examples/xApp/c/monitor/xapp_kpm_moni' 2>/dev/null | head -1"
        file_path = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
        return file_path if file_path else None
    except Exception as e:
        print(f"Erro ao localizar o arquivo: {e}", file=sys.stderr)
        return None

def run_xapp(file_path):
    """Executa o xApp e retorna o output"""
    try:
        result = subprocess.run(
            [file_path],
            capture_output=True,
            text=True,
            timeout=30,
            env={'LD_LIBRARY_PATH': '/usr/local/lib/flexric/'}
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        print("O xApp demorou muito para responder e foi interrompido.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Erro ao executar o xApp: {e}", file=sys.stderr)
        return None

def extract_data(output_text):
    """Extrai todos os dados do output"""
    # Expressões regulares para os dados principais
    patterns = {
        "nearRT-RIC IP": r"nearRT-RIC IP Address\s*=\s*([\d\.]+)",
        "PORT": r"PORT\s*=\s*(\d+)",
        "SM_ID": r"SM ID\s*=\s*(\d+)",
        "with def": r"with def\s*=\s*([\w\-]+)",
        "node_info": r"E2 node (\d+) info: nb_id (\d+), mcc (\d+), mnc (\d+), mnc_digit_len (\d+), ran_type ([\w_]+)",
        "ran_functions": r"E2 node (\d+) supported RAN function's IDs:, ([\d,\s]+)",
        "kpm_metrics": r"(DRB\.[\w]+|RRU\.[\w]+)(?=\s*=)"
    }

    # Coleta de dados básicos
    data = {}
    sm_mapping = {}
    sm_ids = []
    sm_defs = []

    for key, pattern in patterns.items():
        matches = re.findall(pattern, output_text)
        if key == "SM_ID":
            sm_ids = matches
        elif key == "with def":
            sm_defs = matches
        elif matches and key not in ["node_info", "ran_functions", "kpm_metrics"]:
            data[key] = matches[0]

    # Mapeamento de SM_IDs
    if len(sm_ids) == len(sm_defs):
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

    # Verifica se há métricas KPM no output
    kpm_metrics = {}
    if '2' in sm_ids:  # Verifica se o SM ID 2 (KPM) está presente
        kpm_metrics["{#RAN_FUNC_ID}"] = 2
        
        # Lista de métricas KPM que queremos capturar
        desired_metrics = {
            "{#RAN_2_PDCP_DL}": "DRB.PdcpSduVolumeDL",
            "{#RAN_2_PDCP_UL}": "DRB.PdcpSduVolumeUL",
            "{#RAN_2_RLC_DL}": "DRB.RlcSduDelayDl",
            "{#RAN_2_UE_DL}": "DRB.UEThpDl",
            "{#RAN_2_UE_UL}": "DRB.UEThpUl",
            "{#RAN_2_PRB_DL}": "RRU.PrbTotDl",
            "{#RAN_2_PRB_UL}": "RRU.PrbTotUl"
        }
        
        # Verifica quais métricas estão presentes no output
        for key, metric in desired_metrics.items():
            if re.search(rf"{re.escape(metric)}\s*=", output_text):
                kpm_metrics[key] = metric

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

    if kpm_metrics:
        output.append(kpm_metrics)

    return {"data": output}

def main():
    file_path = find_xapp()
    if not file_path:
        print("xApp não encontrado.", file=sys.stderr)
        sys.exit(1)

    output = run_xapp(file_path)
    if not output:
        sys.exit(1)

    try:
        data = extract_data(output)
        print(json.dumps(data, indent=4))
    except Exception as e:
        print(f"Erro ao processar dados: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

