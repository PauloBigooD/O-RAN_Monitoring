import json
import subprocess
import re
import os

# Função para capturar os logs do Docker
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

# Função para enviar dados via zabbix_sender
def send_to_zabbix(data: dict, hostname: str, zabbix_server: str = "172.31.0.61", port: int = 10051):
    zabbix_data = []

    # Formata os dados do gNB
    for gnb in data.get("gNB", []):
        zabbix_data.append(f"{hostname} gNB.Index {gnb['Index']}")
        zabbix_data.append(f"{hostname} gNB.Status {gnb['Status']}")
        zabbix_data.append(f"{hostname} gNB.GlobalID {gnb['Global ID']}")
        zabbix_data.append(f"{hostname} gNB.Name {gnb['gNB Name']}")
        zabbix_data.append(f"{hostname} gNB.PLMN {gnb['PLMN']}")

    # Formata os dados do UE
    for ue in data.get("UE", []):
        zabbix_data.append(f"{hostname} UE.Index {ue['Index']}")
        zabbix_data.append(f"{hostname} UE.5GMMState {ue['5GMM state']}")
        zabbix_data.append(f"{hostname} UE.IMSI {ue['IMSI']}")
        zabbix_data.append(f"{hostname} UE.GUTI {ue['GUTI'] if ue['GUTI'] else 'N/A'}")
        zabbix_data.append(f"{hostname} UE.RANUENGAPID {ue['RAN UE NGAP ID'] if ue['RAN UE NGAP ID'] else 'N/A'}")
        zabbix_data.append(f"{hostname} UE.AMFUEID {ue['AMF UE ID'] if ue['AMF UE ID'] else 'N/A'}")
        zabbix_data.append(f"{hostname} UE.PLMN {ue['PLMN']}")
        zabbix_data.append(f"{hostname} UE.CellID {ue['Cell ID'] if ue['Cell ID'] else 'N/A'}")

    # Salva dados em arquivo temporário para enviar ao Zabbix
    zabbix_input_file = "zabbix_data.txt"
    with open(zabbix_input_file, "w") as file:
        file.write("\n".join(zabbix_data) + "\n")

    # Envia dados para o Zabbix
    try:
        result = subprocess.run([
            "zabbix_sender", "-z", zabbix_server, "-p", str(port), "-T", "-i", zabbix_input_file
        ], capture_output=True, text=True)

        print("Resultado do envio para o Zabbix:")
        print(result.stdout)
        print(result.stderr)
    except FileNotFoundError:
        print("Erro: zabbix_sender não encontrado. Instale o pacote antes de continuar.")
    finally:
        if os.path.exists(zabbix_input_file):
            os.remove(zabbix_input_file)

# Nome do container Docker
container_name = "oai-amf"

# Captura os logs
logs = get_docker_logs(container_name)
if not logs:
    print("Nenhum log capturado ou container não acessível.")
    exit(1)

# Padrões RegEx ajustados para capturar informações relevantes
gnb_pattern = re.compile(r"\|\s+(\d+)\s+\|\s+(Connected|Disconnected)\s+\|\s+([0-9a-fx]+)\s+\|\s+([^|]+)\s+\|\s+([\d, ]+)\s+\|")
ue_pattern = re.compile(r"\|\s*(\d+)\s*\|\s*(5GMM-[A-Z]+)\s*\|\s*(\d+)\s*\|\s*(\d*)\s*\|\s*(\d*)\s*\|\s*(\d*)\s*\|\s*([\d, ]+)\s*\|\s*(\d*)\s*\|")

# Estrutura para armazenar os dados
data = {
    "gNB": [],
    "UE": []
}

# Processamento dos dados do gNB
gnb_matches = list(gnb_pattern.finditer(logs))
if not gnb_matches:
    print("Nenhuma informação de gNB encontrada nos logs.")
for match in gnb_matches:
    index, status, global_id, gnb_name, plmn = match.groups()
    data["gNB"].append({
        "Index": int(index),
        "Status": status,
        "Global ID": global_id,
        "gNB Name": gnb_name.strip(),
        "PLMN": plmn.strip()
    })

# Processamento dos dados do UE
ue_matches = list(ue_pattern.finditer(logs))
if not ue_matches:
    print("Nenhuma informação de UE encontrada nos logs.")
for match in ue_matches:
    index, state, imsi, guti, ran_ue_ngap_id, amf_ue_id, plmn, cell_id = match.groups()
    data["UE"].append({
        "Index": int(index),
        "5GMM state": state,
        "IMSI": imsi,
        "GUTI": guti if guti else None,
        "RAN UE NGAP ID": int(ran_ue_ngap_id) if ran_ue_ngap_id else None,
        "AMF UE ID": int(amf_ue_id) if amf_ue_id else None,
        "PLMN": plmn.strip(),
        "Cell ID": int(cell_id) if cell_id else None
    })

# Gera o JSON formatado
json_output = json.dumps(data, indent=4)

# Salva em arquivo ou imprime na tela
output_file = "oai_amf_data.json"
with open(output_file, "w") as f:
    f.write(json_output)

print(f"Dados extraídos e salvos em {output_file}.")
print(json_output)

# Envia dados para o Zabbix
send_to_zabbix(data, hostname="ric-bigood")

