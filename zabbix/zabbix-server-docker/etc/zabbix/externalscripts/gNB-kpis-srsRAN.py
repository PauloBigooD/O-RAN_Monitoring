#!/usr/bin/env python3

import json
import re
import os
import time
import sys

def exit_with_empty_json():
    """Imprime um JSON com uma lista de dados vazia e encerra o script de forma limpa."""
    print(json.dumps({"data": []}, indent=4))
    sys.exit(0)

# --- Seção 1: Localizar e Validar o Arquivo de Log ---

LOG_FILE = "/tmp/gnb.log"

# Verifica se o arquivo existe
if not os.path.exists(LOG_FILE):
    exit_with_empty_json()

# Verifica se o arquivo foi atualizado recentemente (ex: nos últimos 5 minutos)
# Isso evita que o Zabbix colete dados de uma gNB que pode estar offline.
try:
    # 300 segundos = 5 minutos
    if (time.time() - os.path.getmtime(LOG_FILE)) > 30:
        exit_with_empty_json()
except OSError:
    exit_with_empty_json()

# --- Seção 2: Ler e Processar o Log ---

try:
    with open(LOG_FILE, "r") as f:
        log_text = f.read()
    if not log_text:
        exit_with_empty_json()
except IOError:
    exit_with_empty_json()

# --- Seção 3: Extrair Métricas com Regex ---

# Define os padrões de regex para cada informação desejada
patterns = {
    "{#GNB_PCI}": r"pci:\s*(\d+)",
    "{#GNB_SSB_ARFCN}": r"SSB arfcn:(\d+)",
    "{#GNB_BAND}": r"band:\s*(\d+)",
    "{#GNB_ARFCN}": r"dl_arfcn:\s*(\d+)",
    "{#GNB_SCS}": r"common_scs:\s*(\d+)",
    "{#GNB_NAME}": r"ran_node_name:\s*([\w-]+)"
}

# Dicionário para armazenar os dados encontrados
gnb_data = {}

# Itera sobre os padrões e busca os valores no texto do log
for key, pattern in patterns.items():
    match = re.search(pattern, log_text)
    if match:
        value_str = match.group(1)
        # Converte para inteiro se for numérico, senão mantém como texto
        try:
            gnb_data[key] = int(value_str)
        except ValueError:
            gnb_data[key] = value_str
    else:
        # Se uma chave não for encontrada, atribui um valor padrão
        # para manter a estrutura do JSON consistente.
        if key == "{#GNB_NAME}":
            gnb_data[key] = "" # Padrão para texto
        else:
            gnb_data[key] = 0  # Padrão para números

# --- Seção 4: Gerar a Saída JSON Final ---

# Garante que não retornemos um JSON de zeros se o log estiver malformado
if not gnb_data.get("{#GNB_NAME}") and gnb_data.get("{#GNB_PCI}", 0) == 0:
    exit_with_empty_json()

# Monta o objeto final no formato esperado pelo Zabbix LLD
json_output = {"data": [gnb_data]}

print(json.dumps(json_output, indent=4))
