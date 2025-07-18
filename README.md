# 📡 Monitoramento Unificado de Multiplataformas E2 em Sistemas Open RAN

- Este repositório fornece um arcabouço para **monitoramento unificado de E2 Service Models (E2SMs)** em arquiteturas O-RAN. A solução integra **Zabbix**, **Grafana** e **scripts personalizados**, permitindo descoberta e visualização contínua dos E2SMs disponíveis na rede. Isso facilita o desenvolvimento de xApps e a configuração de testbeds, oferecendo visibilidade em tempo real sobre as capacidades da rede O-RAN.

 - Também estão incluídas ferramentas para **deploy, gerenciamento e automação** de componentes do ecossistema **OpenAirInterface (OAI)**, como EPC 4G, Core 5G, RANs, FlexRIC e xApps.

- A solução pode ser implantada de forma **monolítica ou distribuída**. No cenário demonstrado, distribuído, o testbed utiliza **4 máquinas físicas**:

## 🔧 Arquitetura do Testbed

![Testbed](https://raw.githubusercontent.com/PauloBigooD/O-RAN_Monitoring/refs/heads/main/figs/Test_bed.png)

| Host | IP             | Função               |
|------|----------------|----------------------|
| 1    | 172.31.0.61    | Zabbix Server        |
| 2    | 192.168.70.178 | OAI 5GC + RIC        |
| 3    | 172.31.0.54    | E2 Node gNB Maxwell  |
| 4    | 172.31.0.56    | E2 Node gNB Bell     |

---

## ✅ Requisitos

- Ubuntu 20.04 ou 22.04 (preferência por 20.04)
- Acesso `sudo`
- Ambiente gráfico ou suporte a `tmux`
- `gnome-terminal` (ou `x-terminal-emulator` como fallback)

---

## Passo 1: ⚙️ Ferramentas de Deployment - OpenAirInterface

Clone o repositório:

```bash
git clone https://github.com/PauloBigooD/O-RAN_Monitoring.git
cd O-RAN_Monitoring
```

O script `oai_tools_menu.sh` oferece um **menu interativo** com diversas opções para instalação, execução, logs e gerenciamento dos componentes do OAI.

---

### 📋 Funcionalidades do Menu

| Opção | Ação                                                |
|-------|-----------------------------------------------------|
| 1     | Instalar Docker e UHD 🛠                             |
| 2     | Instalar libuhd 4.4–4.7 📡                          |
| 3     | Ativar modo performance 🚀                          |
| 4     | Instalar dependências do 5GC e RAN                  |
| 5     | Instalar dependências do EPC 4G e RAN               |
| 6–12  | Gerenciar Core 5G e EPC 4G                          |
| 13–18 | Instalar/Iniciar FlexRIC, E2 Agent, gNB, UE, xApps  |
| 19–25 | Inicialização de gNBs/eNBs (Docker e Bare Metal)   |

---

## Passo 2: 🧪 Execução Recomendada Inicial

Antes de iniciar o deploy completo, recomenda-se executar:

```bash
1) Instalar Docker e UHD
2) (opcional) Instalar libuhd 4.4–4.7
3) Ativar modo performance
```

---

##  🏗️ Deploy do Core 5G (5GC)

### Passo 3: 🔧 Instalar dependências

```bash
4) Dependências 5GC e RAN
```
> Para instalação no modo monolítico realize o passo 3.1

> Para instalação no modo distribuído realize o passo 3.2

### Passo 3.1: 📶  Iniciar 5GC - Testbed Monolítico

```bash
6) Iniciar Core 5G Monolítico
```

### Passo 3.1.1: 📜 Visualizar logs do AMF

```bash
8) Logs Core 5G - AMF
```

![AMF-log](https://raw.githubusercontent.com/PauloBigooD/O-RAN_Monitoring/refs/heads/main/figs/5GC-AMF.png)

---

### Passo 3.2: 5GC - Testbed Distribuído
> Essas configurações devem ser aplicadas quando queremos que o CORE receba conexões de gNBs externas.

### Passo 3.2.1: **Criar interface mac-vlan**:
> Os endereços IPs a seguir devem ser configurados conforme as especificações da rede local.
- --subnet= Endereço da rede do Host - (aqui: 192.168.170.0/24)
- --gateway= Gatewai da rede do Host - (aqui: 192.168.170.1)
- parent= Nome da interface de rede do Host - (aqui: enp3s0)

```bash
sudo docker network create -d macvlan --subnet=192.168.170.0/24 --gateway=192.168.170.1 -o parent=enp3s0 macvlan-dhcp
```

### Passo 3.2.2: **Ajustar endereços IP do Docker-Compose**

> Após realizar a configuração da interface `macvlan` é necessário conferir os IPs de cada uma das funções de rede do arquivo `docker-compose-basic-nrf-macvlan.yaml` localizado dentro da pasta `core-scripts`. Após realizar os ajustes salve o arquivo.

> Todos os IPs devem ser ajustados para endereços IP disponíveis na mesma faixa da sua rede.

>  ⚠️ Note que alguns IPs aparecem mais de uma vez. Realize o procedimento de substituição com muito cuidado!

 **Para este deployment foram utilizados os seguintes endereços IP**:

| VNF         | IP
| ----------- | ---------------
|oai-amf      | 192.168.170.178
|oai-nrf      | 192.168.170.179
|oai-udr      | 192.168.170.180
|oai-udm      | 192.168.170.181
|oai-ausf     | 192.168.170.182
|oai-smf      | 192.168.170.183
|oai-spgwu    | 192.168.170.184
|trf-gen-cn5g |192.168.170.185
|mysql        | 192.168.170.186

### Passo 3.2.3: **Ajustar endereços IP do arquivo amf.conf**

> Outro arquivo que exige o ajuste dos IPs é o `amf.conf` localizado em `core-scripts/etc`, os IPs devem ser configurados de acordo com os configurados no passo anterior. Após realizar os ajustes salve o arquivo.

 **Para este deployment foram utilizados os seguintes endereços IP**:

```
      SMF_INSTANCES_POOL = (
        {SMF_INSTANCE_ID = 1; IPV4_ADDRESS = "192.168.170.183"; PORT = "80"; HTTP2_PORT = 8080, VERSION = "v1"; FQDN = "oai-smf", SELECTED = "true"}
      );

    NRF :
    {
      IPV4_ADDRESS = "192.168.170.179";
      PORT         = 80;            # Default: 80
      API_VERSION  = "v1";
      FQDN         = "oai-nrf"
    };

    AUSF :
    {
      IPV4_ADDRESS = "192.168.170.182";
      PORT         = 80;            # Default: 80
      API_VERSION  = "v1";
      FQDN         = "oai-ausf"
    };

    UDM :
    {
      IPV4_ADDRESS = "192.168.170.181";
      PORT         = 80;    # Default: 80
      API_VERSION  = "v2";
      FQDN         = "oai-udm"
    };

    AUTHENTICATION:
    {
        ## MySQL mandatory options
        MYSQL_server = "192.168.170.186"; # MySQL Server address
        MYSQL_user   = "root";   # Database server login
        MYSQL_pass   = "linux";   # Database server password
        MYSQL_db     = "oai_db";     # Your database name
        RANDOM = "true";
    };
```
### Passo 3.2.4: 📶  Iniciar 5GC 

```bash
7) Iniciar Core 5G Distribuido
```

### Passo 3.3: 🛑 Encerrar 5GC

> Para encerra o 5GC selecione a seguinte opção

```bash
10) Parar Core 5G
```
---

## 🧠 Near-RT RIC

### Passo 4: 🧱 Instalar FlexRIC

```bash
12) Instalar FlexRIC
```

> ⚠️ Esse processo o faz rebuild dos componentes da RAN e pode levar alguns minutos.

### Passo 4.1: Iniciar Near-RT RIC - Monolítico

```bash
13) Iniciar nearRT-RIC
```

### Passo 4.2: Near-RT RIC - Distribuído

> Para configurar o Near-RT de maneira distribuída é necessário mudar o endereço IP do arquivo `flexric/flexric.conf`. Mas primeiramente devemos instalar o FlexRIC. 

```bash
12) Instalar FlexRIC
```

> O proximo passo é adcionar um IP à interface de rede local, este será o novo IP do Near-RT RIC. 

```bash
sudo ip addr add 192.168.170.187/24 dev enp3s0
```

> Após adicionar o IP edite o arquivo `flexric/flexric.conf`. Após realizar os ajustes salve o arquivo.

```bash
[NEAR-RIC]
NEAR_RIC_IP = 127.0.0.1 # Substitua pelo IP que foi adicionado a interface local
```

### Passo 4.2.1: Build Near-RT RIC manualmente

> Primeiramente devemos remover a pasta `flexric/build`

```bash
sudo rm -rf flexric/build
```
> Rebuild o FlexRIC

```bash
mkdir flexric/build
cd flexric/build && sudo cmake .. && sudo make -j8 && sudo make install && cd ../..
```

### Passo 4.2.2: Iniciar Near-RT RIC - Distribuído

```bash
13) Iniciar nearRT-RIC
```

---

## 📡 RAN (E2 Node)

### Passo 5.1: 🗼 Testbed Monolítico

> ⚠️ Se o Core 5G e a RAN estiverem na mesma máquina, apenas execute:

```bash
15) Iniciar gNB rfsim
```

### Passo 5.2: 🗼 Testbed Distribuído

Em hosts dedicados à RAN:

```bash
1) Instalar Docker e UHD
3) Modo performance
12) Instalar FlexRIC
```



## Passo 5.3 📄 Ajuste de IPs

> ⚠️ Para deployment Monolitico não é necessário alterar.

Verifique os arquivos de configuração na pasta `conf/b210PRB106.conf` para ajustar os IPs conforme seu ambiente:

```conf
amf_ip_address = ( { ipv4 = "192.168.170.178"; ... } ); # Iforme o IP do AMF

NETWORK_INTERFACES:
{
    GNB_INTERFACE_NAME_FOR_NG_AMF = "enp3s0"; # Deve ser a mesma do computador local
    GNB_IPV4_ADDRESS_FOR_NG_AMF   = "192.168.170.78/24";
    ...
};
```

> ⚠️ Certifique-se de ajustar `eth0` e os IPs para as interfaces reais do host nos casos de deploy bare metal.

### Passo 5.4: Iniciar gNB 

> Selecione uma das seguintes opções:

```bash
18) Iniciar gNB n310 106 PRBs (Bare Metal)
19) Iniciar gNB n310 162 PRBs (Bare Metal)
20) Iniciar gNB n310 273 PRBs (Bare Metal)
21) Iniciar gNB b210 106 PRBs (Bare Metal)
22) Iniciar gNB b210 106 PRBs (Docker 🐳)
```
> ⚠️ Por questões de estabilidade, recomenda-se a seleção da opção 21 `gNB b210 106 PRBs (Bare Metal)`

---

## Zabbix Server / Grafana

> ⚠️ É recomendado dedicar um Host ou uma Máquina Virtual para a instalação do Zabbix Server.

```bash
cd zabbix/zabbix-server-docker
```

> Caso o Host não tenha o Docker instalado utilize o script `install-docker.sh` e realize a instalação.

### Passo 6: Iniciar Zabbix Server

```bash
cd docker compose up -d
```

## Zabbix Agent


#
## 📬 Contato

- 📧 Email: [paulo.eduardo.093@ufrn.edu.br](mailto:paulo.eduardo.093@ufrn.edu.br)
- 💼 LinkedIn: [paulo-eduardo-5a18b3174](https://linkedin.com/in/paulo-eduardo-5a18b3174)
- 💻 GitHub: [@PauloBigooD](https://github.com/PauloBigooD)

---

## 🙌 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma [issue](https://github.com/PauloBigooD/O-RAN_Monitoring/issues) ou enviar um pull request com melhorias, correções ou novos módulos.