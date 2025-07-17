# Monitoramento Unificado para Multiplataformas E2 em Sistemas Open RAN


Este repositório apresenta um arcabouço para monitoramento unificado de E2 Service Models (E2SMs) em arquiteturas O-RAN. A proposta utiliza `Zabbix` e `Grafana` integrados com scripts personalizados, para buscar e visualizar os E2SMs disponíveis na rede. Essa implementação permite o acompanhamento contínuo das capacidades expostas pela rede O-RAN, auxiliando no desenvolvimento de xApps e na configuração de testbeds.

 Ele também contém um conjunto de ferramentas para facilitar o deploy, gerenciamento e automação de elementos do ecossistema **OpenAirInterface (OAI)**, incluindo EPC 4G, Core 5G, RANs e integrações com FlexRIC e xApps.

 Pode ser instalado de forma monolitica ou distribuída. Para o meu caso de uso o testbed ficou da seguinte forma:

| Host | IP             |  Função              |  
| ---- | -------------- | -------------------- |
| 1    | 172.31.0.61    | Zabbix Server        |
| 2    | 192.168.70.178 | OAI 5GC + RIC        |
| 3    | 172.31.0.54    | E2 Node gNB Maxwell  |
| 4    | 172.31.0.56    | E2 Node gNB Bell     |



## 🧠 Requisitos
- Ubuntu 20.04 ou 22.04 (preferência por 20.04 para máxima compatibilidade)
- Acesso sudo
- Ambiente gráfico ou suporte ao tmux
- gnome-terminal (ou x-terminal-emulator no fallback)

## 🛠 - OpenAirInterface Deployment Tools






### 🚀 Como começar

#### Clone o repositório:

```bash
git clone https://github.com/PauloBigooD/O-RAN_Monitoring.git
cd  O-RAN_Monitoring
```

Ao acessar o repositório temos o script `oai_tools_menu.sh` que possui um menu interativo com diversas opções para instalação, execução, logs e gerenciamento de componentes OAI. 


### 📋 O que o menu oferece?

| Opção | Ação                                               |
| ----- | -------------------------------------------------- |
| 1     | Instalar componentes Git, Docker e UHD 🛠 
| 2     | Instalar libuhd 4.4–4.7 📡
| 3     | Modo performance 🚀
| 4     | Dependências 5GC e RAN
| 5     | Dependências 4G EPC e RAN
| 6     | Iniciar Core 5G
| 7     | Iniciar EPC 4G
| 8     | Logs Core 5G - AMF
| 9     | Logs EPC 4G - MME
| 10    | Parar Core 5G
| 11    | Parar EPC 4G
| 12    | Instalar FlexRIC
| 13    | Iniciar nearRT-RIC
| 14    | Iniciar E2 Node Agent
| 15    | Iniciar gNB rfsim
| 16    | Iniciar UE rfsim
| 17    | Iniciar xApps
| 18–24 | Inicialização de gNBs e eNBs (bare metal e docker) |

--- 

### 🚧 Primeira execução (recomendado)

Para garantir que seu ambiente esteja pronto, execute as opções 1, 2 e 3 antes de usar os demais recursos. Essas opções preparam seu sistema com as dependências básicas necessárias para uso completo da suíte OAI.

```bash
1) Instalar Git, Docker e UHD 🛠
2) Instalar libuhd 4.4–4.7 📡
3) Modo performance 🚀
```
---

## 📡 Instalar/Iniciar 5GC e RAN

**5GC**: Para realizar o provisionamento do OAI 5GC devemos escolher a opção 4 do menu, responsável por instalar as dependências referentes ao CORE e RAN.

### ⏳ Instalando as dependências do 5GC e RAN

```bash
4) Dependências 5GC e RAN
```

### ⌛ Iniciando 5GC

Após concluir a instalação das dependências já podemos iniciar o 5GC selecionando a opção 6 do menu. 

```bash
6) Iniciar Core 5G
```

Os logs do AMF podem ser visualizados selecionando a opção 8. Para encerrar o 5GC selecione a opção 10 do menu.

```bash
8) Logs Core 5G - AMF
```
Para encerrar o 5GC selecione a opção 10 do menu.

```bash
10) Parar Core 5G
```


## 📊 Instalar/Iniciar Near-RT RIC

**Near-RT RIC**: A instalação dos componentes do Near-RT RIC é feita a partir da seleção da opção 12 do menu.

### ⏳ Instalando as dependências do Near-RT RIC

```bash
12) Instalar FlexRIC
```
### ⌛ Iniciando o FlexRIC

Após concluir a instalação do FlexRIC já podemos iniciar o Near-RT RIC selecionando a opção 13 do menu.

```bash
13) Iniciar nearRT-RIC
```

## 👀 Conferindo IPs

É importante realizar a conferência dos endereços IPs presentes nos arquivos de configuração da gNB localizados em `conf`. Observe que nessa pasta exitem arquivos de configuração para os diferentes modelos de gNB para provisionamento via Docker ou Bare Metal. Aqui estão alguns dos parâmetros que devem ser ajustados:

```conf
    ////////// AMF parameters:
    amf_ip_address      = ( { ipv4       = "192.168.70.132"; # Aqui deve ser o IP do AMF
                              ipv6       = "192:168:30::17";
                              active     = "yes";
                              preference = "ipv4";
                            }
                          );


    NETWORK_INTERFACES :
    {
        GNB_INTERFACE_NAME_FOR_NG_AMF            = "eth0";  # Para deplyment Bare Metal ajustar para a interface do Host
        GNB_IPV4_ADDRESS_FOR_NG_AMF              = "192.168.70.150/24"; # Para deplyment Bare Metal ajustar para o IP do Host
        GNB_INTERFACE_NAME_FOR_NGU               = "eth0";  # Para deplyment Bare Metal ajustar para a interface do Host
        GNB_IPV4_ADDRESS_FOR_NGU                 = "192.168.70.150/24";  # Para deplyment Bare Metal ajustar para o IP do Host
        GNB_PORT_FOR_S1U                         = 2152; 
    };

```

## 📬 Contato

- 📧 Email: paulo.eduardo.093@ufrn.edu.br
- 💼 LinkedIn: paulo-eduardo-5a18b3174
- 💻 GitHub: PauloBigooD

### 🙌 Contribuições
- Sinta-se à vontade para abrir issues ou pull requests! Sugestões de melhoria, correções e novos módulos são bem-vindos.