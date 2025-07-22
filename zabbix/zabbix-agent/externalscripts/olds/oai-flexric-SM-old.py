#!/usr/bin/env python3

import subprocess
import json
import re

# Comando para encontrar o caminho do arquivo
cmd = "find / -type f -wholename '*/build/examples/xApp/python3/xapp_mac_rlc_pdcp_gtp_moni.py' 2>/dev/null"

try:
    file_path = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
    if not file_path:
        print("Arquivo não encontrado.")
        exit(1)
except Exception as e:
    print("Erro ao localizar o arquivo:", e)
    exit(1)

# Executa o script e captura as primeiras 30 linhas
try:
    result = subprocess.run(
        ["python3", file_path],
        capture_output=True,
        text=True,
        timeout=30  # Ajustado para 30 segundos
    )
    output_lines = result.stdout.splitlines()[:30]  # Pegando apenas as 30 primeiras linhas
except subprocess.TimeoutExpired:
    print("O script demorou muito para responder e foi interrompido.")
    exit(1)
except Exception as e:
    print("Erro ao executar o script:", e)
    exit(1)

# Unindo as linhas em um único texto para facilitar a busca com regex
output_text = "\n".join(output_lines)

# Expressões regulares para extração
patterns = {
    "nearRT-RIC IP": r"nearRT-RIC IP Address\s*=\s*([\d\.]+)",
    "PORT": r"PORT\s*=\s*(\d+)",
    "SM_ID": r"SM ID\s*=\s*(\d+)",
    "with def": r"with def\s*=\s*([\w\-]+)"
}

# Dicionário para armazenar os dados coletados
data = {}
sm_mapping = {}

# Extração dos dados
for key, pattern in patterns.items():
    matches = re.findall(pattern, output_text)
    if key == "SM_ID" and matches:
        sm_ids = matches
    elif key == "with def" and matches:
        sm_defs = matches
    elif matches:
        data[key] = matches[0]  # Apenas um valor esperado

# Mapeamento entre SM_ID e suas definições
if "sm_ids" in locals() and "sm_defs" in locals() and len(sm_ids) == len(sm_defs):
    for sm_id, sm_def in zip(sm_ids, sm_defs):
        sm_mapping[f"{{#SM_ID_{sm_id}}}"] = sm_def

# Criando o JSON final
json_data = {
    "data": [
        sm_mapping
    ]
}

# Adiciona o IP e a PORTA ao JSON se encontrados
if "nearRT-RIC IP" in data and "PORT" in data:
    json_data["data"][0].update({
        "{#NEAR_RT_RIC_IP}": data["nearRT-RIC IP"],
        "{#PORT}": data["PORT"]
    })

# Imprime JSON formatado
print(json.dumps(json_data, indent=4))

