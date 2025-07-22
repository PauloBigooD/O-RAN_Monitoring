import os
import time
import json
import requests
from time import sleep

ZABBIX_URL = os.environ.get("ZABBIX_URL", "http://172.18.0.1/api_jsonrpc.php")
ZABBIX_USER = os.environ.get("ZABBIX_USER", "Admin")
ZABBIX_PASSWORD = os.environ.get("ZABBIX_PASSWORD", "zabbix")
TEMPLATE_DIR = os.environ.get("TEMPLATE_DIR", "/templates")
TEMPLATE_NAMES = [
    "ICMP Ping",                   
    "Template Linux Disk IO",      
    "Linux CPU Core - Ativo",      
    "O-RAN 5G monitoring - OAI"    
]
    # Lista de templates na ordem desejada
TEMPLATES_TO_LINK = [
    "Linux CPU Core - Ativo", 
    #"Template Linux Disk IO",
    "Docker by Zabbix agent 2",
    "ICMP Ping"
]

def wait_for_zabbix(session, retries=30, delay=5):
    print("⏳ Aguardando Zabbix responder...")
    for i in range(retries):
        try:
            response = session.post(ZABBIX_URL, json={
                "jsonrpc": "2.0",
                "method": "apiinfo.version",
                "params": {},
                "id": 1
            }, timeout=5)
            if response.ok:
                version = response.json().get("result", "")
                print(f"✅ Zabbix pronto! Versão: {version}")
                return version
        except Exception:
            pass
        time.sleep(delay)
    raise RuntimeError("❌ Timeout ao aguardar Zabbix responder.")

def login(session):
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": ZABBIX_USER,
            "password": ZABBIX_PASSWORD
        },
        "id": 1
    }
    response = session.post(ZABBIX_URL, json=payload)
    print("🔐 Resposta do login:", response.text)
    return response.json()["result"]


def get_zabbix_server_host(session, token):
    """Função robusta para encontrar o host Zabbix server"""
    # Tentativa 1: Busca direta pelo nome exato
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "filter": {"host": "Zabbix server"},
            "output": ["hostid", "host", "name"],
            "selectInterfaces": ["ip"]
        },
        "id": 3
    }
    
    headers = {
        "Content-Type": "application/json-rpc",
        "Authorization": f"Bearer {token}"
    }
    
    response = session.post(ZABBIX_URL, json=payload, headers=headers)
    result = response.json()
    
    if result.get("result"):
        host = result["result"][0]
        print(f"✅ Host encontrado - ID: {host['hostid']}, IP: {host['interfaces'][0]['ip']}")
        return host["hostid"]
    
    # Tentativa 2: Busca mais ampla
    print("⚠️ Busca direta falhou, tentando busca ampla...")
    payload["params"]["filter"] = {}  # Remove filtro
    payload["params"]["search"] = {"host": "zabbix"}  # Busca parcial
    payload["params"]["searchWildcardsEnabled"] = True
    
    response = session.post(ZABBIX_URL, json=payload, headers=headers)
    result = response.json()
    
    if result.get("result"):
        for host in result["result"]:
            if "zabbix" in host["host"].lower():
                print(f"✅ Host similar encontrado - {host['host']} (ID: {host['hostid']})")
                return host["hostid"]
    
    # Se ainda não encontrou, mostra todos os hosts para diagnóstico
    print("🔍 Listando todos os hosts para diagnóstico:")
    payload["params"] = {
        "output": ["hostid", "host", "name"],
        "selectInterfaces": ["ip"]
    }
    
    response = session.post(ZABBIX_URL, json=payload, headers=headers)
    all_hosts = response.json().get("result", [])
    
    for host in all_hosts:
        print(f"- {host['host']} (ID: {host['hostid']}, IP: {host['interfaces'][0]['ip']})")
    
    raise RuntimeError("Host 'Zabbix server' não encontrado. Verifique a lista acima.")


def import_template(session, token, template_path, zbx_version):
    with open(template_path, "r", encoding='utf-8') as f:
        template_data = f.read()

    rules = {
        "templates": {"createMissing": True, "updateExisting": True},
        "template_groups": {"createMissing": True},
        "items": {"createMissing": True, "updateExisting": True},
        "discoveryRules": {"createMissing": True, "updateExisting": True},
        "triggers": {"createMissing": True, "updateExisting": True},
        "graphs": {"createMissing": True, "updateExisting": True},
        "valueMaps": {"createMissing": True, "updateExisting": True},
        "httptests": {"createMissing": True, "updateExisting": True}
    }

    payload = {
        "jsonrpc": "2.0",
        "method": "configuration.import",
        "params": {
            "format": "yaml",
            "rules": rules,
            "source": template_data
        },
        "id": 2
    }

    headers = {
        "Content-Type": "application/json-rpc",
        "Authorization": f"Bearer {token}"
    }

    response = session.post(ZABBIX_URL, json=payload, headers=headers)
    resp_json = response.json()

    if "error" in resp_json:
        error_msg = json.dumps(resp_json['error'], indent=2)
        raise RuntimeError(f"Erro ao importar {template_path}:\n{error_msg}")

    print(f"[✓] Importado: {os.path.basename(template_path)}")


def get_template_ids(session, token, template_names):
    """Função otimizada para encontrar templates com nomes exatos"""
    print("\n🔍 Buscando templates com correspondência exata...")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "template.get",
        "params": {
            "output": ["templateid", "name"],
            "filter": {"name": template_names},
            "searchWildcardsEnabled": False
        },
        "id": 4
    }
    
    headers = {
        "Content-Type": "application/json-rpc",
        "Authorization": f"Bearer {token}"
    }
    
    response = session.post(ZABBIX_URL, json=payload, headers=headers)
    result = response.json()
    
    if not result.get("result"):
        # Lista todos os templates para ajudar no diagnóstico
        print("\n🔍 Todos os templates disponíveis:")
        all_templates = session.post(ZABBIX_URL, json={
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": ["templateid", "name"],
                "sortfield": "name"
            },
            "id": 5
        }, headers=headers).json().get("result", [])
        
        for tpl in all_templates:
            print(f"- {tpl['name']} (ID: {tpl['templateid']})")
        
        raise RuntimeError(f"Não encontrou templates com os nomes exatos: {template_names}")
    
    print("✅ Templates encontrados:")
    template_map = {tpl['name']: tpl['templateid'] for tpl in result["result"]}
    for name, tid in template_map.items():
        print(f"- {name} (ID: {tid})")
    
    return list(template_map.values())

def main():
    # [Restante do código permanece igual...]
    try:
        print("\n🔍 Obtendo host 'Zabbix server'...")
        host_id = get_zabbix_server_host(session, token)
        
        print("\n🔍 Buscando templates para vincular...")
        template_ids = get_template_ids(session, token, TEMPLATES_TO_LINK)
        
        update_host_templates(session, token, host_id, template_ids)
    except Exception as e:
        print(f"[!] Falha ao vincular templates: {e}")
        # Sugere ajustes específicos baseados nos nomes reais
        print("\n💡 Dica: Ajuste a lista TEMPLATE_NAMES para corresponder exatamente aos nomes listados acima")

def update_host_configuration(session, token, host_id):
    """Atualiza a configuração do host (IP e templates)"""
    print(f"\n🔧 Configurando host {host_id}...")
    
    # 1. Primeiro atualiza o IP da interface
    update_host_ip(session, token, host_id)
    
    # 2. Depois vincula os templates de forma segura
    update_host_templates_safely(session, token, host_id)

def update_host_ip(session, token, host_id):
    """Atualiza o IP da interface do host para 172.18.0.1"""
    print("🔄 Atualizando IP do host para 172.18.0.1...")
    
    # Obter interface ID
    payload = {
        "jsonrpc": "2.0",
        "method": "hostinterface.get",
        "params": {
            "hostids": host_id,
            "output": ["interfaceid"]
        },
        "id": 7
    }
    
    headers = {
        "Content-Type": "application/json-rpc",
        "Authorization": f"Bearer {token}"
    }
    
    response = session.post(ZABBIX_URL, json=payload, headers=headers)
    interface_id = response.json()["result"][0]["interfaceid"]
    
    # Atualizar interface
    payload = {
        "jsonrpc": "2.0",
        "method": "hostinterface.update",
        "params": {
            "interfaceid": interface_id,
            "ip": "172.18.0.1",
            "dns": "",
            "port": "10050",
            "useip": 1
        },
        "id": 8
    }
    
    response = session.post(ZABBIX_URL, json=payload, headers=headers)
    if "error" in response.json():
        print(f"⚠️ Aviso: Não foi possível atualizar o IP: {response.json()['error']}")
    else:
        print("✅ IP atualizado com sucesso!")

def update_host_templates_sequential(session, token, host_id):
    """Vincula templates um por um de forma sequencial"""
    print("\n🔗 Iniciando vinculação sequencial de templates...")
    
    headers = {
        "Content-Type": "application/json-rpc",
        "Authorization": f"Bearer {token}"
    }
    
    # Obter IDs dos templates
    print("\n🔍 Obtendo IDs dos templates...")
    template_ids = {}
    for template_name in TEMPLATES_TO_LINK:
        payload = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": ["templateid"],
                "filter": {"name": template_name}
            },
            "id": 9
        }
        response = session.post(ZABBIX_URL, json=payload, headers=headers)
        if response.json().get("result"):
            template_ids[template_name] = response.json()["result"][0]["templateid"]
            print(f"- {template_name} (ID: {template_ids[template_name]})")
        else:
            print(f"⚠️ Template {template_name} não encontrado")
    
    # Vincular templates de forma cumulativa
    print("\n⚙️ Vinculando templates...")
    success_count = 0
    
    # Primeiro obtém os templates atuais
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "hostids": host_id,
            "output": ["hostid"],
            "selectParentTemplates": ["templateid"]
        },
        "id": 10
    }
    response = session.post(ZABBIX_URL, json=payload, headers=headers)
    current_templates = [{"templateid": t["templateid"]} for t in response.json()["result"][0]["parentTemplates"]]
    
    # Adiciona os novos templates à lista atual
    new_templates = current_templates.copy()
    for template_name, template_id in template_ids.items():
        if {"templateid": template_id} not in new_templates:
            new_templates.append({"templateid": template_id})
    
    # Se não há novos templates para adicionar
    if len(new_templates) == len(current_templates):
        print("✓ Todos os templates já estão vinculados")
        return True
    
    # Tenta atualizar com todos os templates (atuais + novos)
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": host_id,
                "templates": new_templates
            },
            "id": 11
        }
        response = session.post(ZABBIX_URL, json=payload, headers=headers)
        result = response.json()
        
        if "error" in result:
            print(f"❌ Falha ao vincular templates: {result['error']['data']}")
            return False
        else:
            print("✅ Templates vinculados com sucesso!")
            return True
            
    except Exception as e:
        print(f"⚠️ Erro ao vincular templates: {str(e)}")
        return False

def main():
    session = requests.Session()
    zbx_version = wait_for_zabbix(session)
    token = login(session)
    
    # Importar templates
    success = 0
    failures = []
    for f in sorted(os.listdir(TEMPLATE_DIR)):
        if f.endswith(".yaml") or f.endswith(".yml"):
            try:
                import_template(session, token, os.path.join(TEMPLATE_DIR, f), zbx_version)
                success += 1
            except Exception as e:
                print(f"[✗] Falha ao importar {f}: {e}")
                failures.append(f)
    
    # Configurar host
    try:
        print("\n🔍 Obtendo host 'Zabbix server'...")
        host_id = get_zabbix_server_host(session, token)
        
        # 1. Atualizar IP do host
        print("\n🔧 Atualizando configurações do host...")
        update_host_ip(session, token, host_id)
        
        # 2. Vincular templates sequencialmente
        print("\n🔗 Iniciando vinculação de templates...")
        linking_success = update_host_templates_sequential(session, token, host_id)
        
        if not linking_success:
            print("\n⚠️ Atenção: Nem todos os templates foram vinculados corretamente!")
            print("   Verifique as mensagens acima para detalhes.")
        
    except Exception as e:
        print(f"[!] Falha durante configuração do host: {e}")
        failures.append("configuração do host")

    # Relatório final
    print(f"\n✅ Importação finalizada: {success} templates importados com sucesso.")
    if failures:
        print(f"❌ Falhas ocorridas durante: {', '.join(failures)}")
    
    return 0 if not failures else 1

if __name__ == "__main__":
    main()