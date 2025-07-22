import os
import time
import json
import requests

ZABBIX_URL = os.environ.get("ZABBIX_URL", "http://172.18.0.1/api_jsonrpc.php")
ZABBIX_USER = os.environ.get("ZABBIX_USER", "Admin")
ZABBIX_PASSWORD = os.environ.get("ZABBIX_PASSWORD", "zabbix")
TEMPLATE_DIR = os.environ.get("TEMPLATE_DIR", "/templates")
ZABBIX_HOSTNAME = os.environ.get("ZABBIX_HOSTNAME", "Zabbix server")
TEMPLATE_NAMES = [
    "Docker by Zabbix agent 2",
    "Template ICMP Ping",
    "Template Linux Disk IO",
    "Linux Host - Ativo",
    "Zabbix server health"
]

def wait_for_zabbix(session, retries=30, delay=5):
    print("\u23f3 Aguardando Zabbix responder...")
    for i in range(retries):
        try:
            response = session.post(ZABBIX_URL, json={
                "jsonrpc": "2.0",
                "method": "apiinfo.version",
                "params": {},
                "id": 1
            }, timeout=5)
            if response.ok:
                print("✅ Zabbix pronto!")
                return
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

def list_all_hosts(session, token):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host", "name"]
        },
        "auth": token,
        "id": 99
    }
    response = session.post(ZABBIX_URL, json=payload)
    result = response.json().get("result", [])
    
    print("\n📋 Hosts encontrados no Zabbix:")
    for h in result:
        print(f"- ID: {h['hostid']}, host: '{h['host']}', name: '{h['name']}'")
    return result

def list_all_templates(session, token):
    payload = {
        "jsonrpc": "2.0",
        "method": "template.get",
        "params": {
            "output": ["templateid", "host", "name"]
        },
        "auth": token,
        "id": 5
    }
    response = session.post(ZABBIX_URL, json=payload)
    templates = response.json().get("result", [])
    
    print("📋 Templates disponíveis no Zabbix:")
    for t in templates:
        print(f"- ID: {t['templateid']}, host: '{t['host']}', name: '{t['name']}'")
    
    return templates


def import_template(session, token, template_path):
    with open(template_path, "r") as f:
        template_data = f.read()

    payload = {
        "jsonrpc": "2.0",
        "method": "configuration.import",
        "params": {
            "format": "yaml",
            "rules": {
                "templates": {"createMissing": True, "updateExisting": True},
                "groups": {"createMissing": True},
                "applications": {"createMissing": True},
                "items": {"createMissing": True, "updateExisting": True},
                "discoveryRules": {"createMissing": True, "updateExisting": True},
                "triggers": {"createMissing": True, "updateExisting": True},
                "valueMaps": {"createMissing": True, "updateExisting": True},
                "graphs": {"createMissing": True, "updateExisting": True},
                "httptests": {"createMissing": True, "updateExisting": True}
            },
            "source": template_data
        },
        "auth": token,
        "id": 2
    }

    response = session.post(ZABBIX_URL, json=payload)
    if "error" in response.json():
        raise RuntimeError(f"Erro ao importar {template_path}: {response.json()['error']}")
    print(f"[\u2713] Importado: {os.path.basename(template_path)}")

def get_host_id(session, token, hostname):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host", "name"]
        },
        "auth": token,
        "id": 3
    }
    response = session.post(ZABBIX_URL, json=payload)
    hosts = response.json().get("result", [])

    for h in hosts:
        if h["host"] == hostname or h["name"] == hostname:
            return h["hostid"]
    return None

def get_template_ids(session, token, template_names):
    payload = {
        "jsonrpc": "2.0",
        "method": "template.get",
        "params": {
            "output": ["templateid", "name"],
            "filter": {"name": template_names}
        },
        "auth": token,
        "id": 4
    }
    response = session.post(ZABBIX_URL, json=payload).json()
    if not response.get("result"):
        raise RuntimeError("Nenhum dos templates foi encontrado.")
    return [tpl["templateid"] for tpl in response["result"]]

def update_host_templates(session, token, host_id, template_ids):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.update",
        "params": {
            "hostid": host_id,
            "templates": [{"templateid": tid} for tid in template_ids]
        },
        "auth": token,
        "id": 5
    }
    response = session.post(ZABBIX_URL, json=payload).json()
    if "error" in response:
        raise RuntimeError(f"Erro ao atualizar host: {response['error']}")
    print("\n✅ Templates vinculados ao host com sucesso!")

def main():
    session = requests.Session()
    wait_for_zabbix(session)
    token = login(session)
    # Chamada temporária para debug:
    # list_all_hosts(session, token)
    templates = list_all_templates(session, token)
    for f in sorted(os.listdir(TEMPLATE_DIR)):
        if f.endswith(".yaml") or f.endswith(".yml"):
            try:
                import_template(session, token, os.path.join(TEMPLATE_DIR, f))
            except Exception as e:
                print(f"[\u2717] Falha ao importar {f}: {e}")

    try:
        host_id = get_host_id(session, token, ZABBIX_HOSTNAME)
        template_ids = get_template_ids(session, token, TEMPLATE_NAMES)
        update_host_templates(session, token, host_id, template_ids)
    except Exception as e:
        print(f"[!] Falha ao ajustar host: {e}")

    print("\n📄 Processo finalizado com sucesso.")

if __name__ == "__main__":
    main()