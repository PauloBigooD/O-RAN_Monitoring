import os
import time
import json
import requests

ZABBIX_URL = os.environ.get("ZABBIX_URL", "http://172.18.0.1/api_jsonrpc.php")
ZABBIX_USER = os.environ.get("ZABBIX_USER", "Admin")
ZABBIX_PASSWORD = os.environ.get("ZABBIX_PASSWORD", "zabbix")
TEMPLATE_DIR = os.environ.get("TEMPLATE_DIR", "/templates")

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

def import_template(session, token, template_path, zbx_version):
    with open(template_path, "r", encoding='utf-8') as f:
        template_data = f.read()

    # Configuração das regras de importação para Zabbix 7.4.0
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

    # Estrutura do payload para Zabbix 7.4.0
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

    # Configuração de headers para Zabbix 7.4.0
    headers = {
        "Content-Type": "application/json-rpc",
        "Authorization": f"Bearer {token}"
    }

    response = session.post(
        ZABBIX_URL,
        json=payload,
        headers=headers
    )
    
    resp_json = response.json()

    if "error" in resp_json:
        error_msg = json.dumps(resp_json['error'], indent=2)
        raise RuntimeError(f"Erro ao importar {template_path}:\n{error_msg}")

    print(f"[✓] Importado: {os.path.basename(template_path)}")

def main():
    session = requests.Session()
    zbx_version = wait_for_zabbix(session)
    
    token = login(session)
    
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

    print(f"\n✅ Importação finalizada: {success} templates importados com sucesso.")
    if failures:
        print(f"❌ Falha ao importar os seguintes templates: {failures}")

if __name__ == "__main__":
    main()