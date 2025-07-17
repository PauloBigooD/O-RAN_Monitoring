#!/usr/bin/env python3

## Author:   Paulo Eduardo da Silva Junior - paulo.eduardo.093@ufrn.edu.br - Tel: +55 (84) 9 8808-0933
## GitHub:   https://github.com/PauloBigooD
## Linkedin: https://www.linkedin.com/in/paulo-eduardo-5a18b3174

import json
import subprocess
import re

def get_docker_logs(container_name: str, tail: int = 11) -> str:
    try:
        logs = subprocess.check_output(
            ["docker", "logs", container_name, "--tail", str(tail)], 
            stderr=subprocess.STDOUT, text=True
        )
        return logs
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando Docker: {e.output}")
        return ""

container_name = "oai-amf"
logs = get_docker_logs(container_name)
if not logs:
    print("Nenhum log capturado ou container não acessível.")
    exit(1)

gnb_pattern = re.compile(r"\|\s+(\d+)\s+\|\s+(Connected|Disconnected)\s+\|\s+([0-9a-fx]+)\s+\|\s+([^|]+)\s+\|\s+([\d, ]+)\s+\|")

data = {"data": []}

gnb_matches = list(gnb_pattern.finditer(logs))
#if not gnb_matches:
#    print("Nenhuma informação de gNB encontrada nos logs.")
    
for match in gnb_matches:
    index, status, global_id, gnb_name, plmn = match.groups()
    data["data"].append({
        "{#GNB_INDEX}": int(index),
        "{#GNB_STATUS}": status,
        "{#GNB_ID}": global_id,
        "{#GNB_NAME}": gnb_name.strip(),
        "{#GNB_PLMN}": plmn.strip()
    })

json_output = json.dumps(data, indent=4)

output_file = "/tmp/oai_amf_gnb.json"
with open(output_file, "w") as f:
    f.write(json_output)

print(json_output)
