# What is [![Zabbix](https://img.shields.io/badge/ZABBIX-FF0000?style=plastic&logo=zotero&logoColor=write)]()?

## Zabbix Server / Grafana

> ⚠️ É recomendado dedicar um Host ou uma Máquina Virtual para a instalação do Zabbix Server.

#### Alterne para o seguinte diretório:

```bash
cd zabbix/zabbix-server-docker
```

> Caso o Host não tenha o Docker instalado utilize o script `install-docker.sh` e realize a instalação.

### Passo 6: Iniciar Zabbix Server

```bash
sudo docker compose up -d
```

> Após executar o deployment do docker-compose as APIs do Zabbix e Grafana estarão disponíveis no IP local da Host. O acesso é feito a partir do navegador WEB.


`Zabbix: 192.168.170.78`

`Username: Admin`

`Password: zabbix`

<img src="https://raw.githubusercontent.com/PauloBigooD/O-RAN_Monitoring/refs/heads/main/figs/Zabbix_API.png">

---

`Grafana: 192.168.170.78:3000`

`Username: admin`

`Password: Grafana`

#### Dashboard Zabbix Server
<img src="https://raw.githubusercontent.com/PauloBigooD/O-RAN_Monitoring/refs/heads/main/figs/Dashboard_Zabbix-Server.png">

#### Dashboard E2 Node
<img src="https://raw.githubusercontent.com/PauloBigooD/O-RAN_Monitoring/refs/heads/main/figs/Dashboard.png">


## Passo 7: Zabbix Agent

A instalação do Zabbix Agent deve ser realizada nos Hosts onde o 5GC foi instalado e no E2 Node. Para instalar o Zabbix Agent é bem simples, basta alternar para `zabbix/zabbix-agent` e executar o script `install_zabbix_agent2.sh`

### Passo 7.2: Alterne para o seguinte diretório:

```bash
cd zabbix/zabbix-agent
```

### Passo 7.2: Instalar Zabbix Agent

 - --hostname = Nome do Host/5GC/E2 Node, que desejamos monitorar

```bash
sudo ./install_zabbix_agent2.sh --hostname "HOST_NAME" --server "IP_ZABBIX-SERVER" --metadata "O-RAN"
```

> Após a instalação do Zabbix Agent o Host estará disponível no Zabbix Server

#### Zabbix Hosts
<img src="https://raw.githubusercontent.com/PauloBigooD/O-RAN_Monitoring/refs/heads/main/figs/Dashboard.png">