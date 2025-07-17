# 🛠 OpenAirInterface Deployment Tools

Este repositório contém um conjunto de ferramentas para facilitar o deploy, gerenciamento e automação de elementos do ecossistema **OpenAirInterface (OAI)**, incluindo EPC 4G, Core 5G, RANs e integrações com FlexRIC e xApps.

---

## 🧠 Requisitos
- Ubuntu 20.04 ou 22.04 (preferência por 20.04 para máxima compatibilidade)
- Acesso sudo
- Ambiente gráfico ou suporte ao tmux
- gnome-terminal (ou x-terminal-emulator no fallback)

## 🚀 Como começar

### Clone o repositório:

```bash
git clone https://github.com/PauloBigooD/OpenAirInterface.git
cd OpenAirInterface
```

## 📋 O que o menu oferece?

O script `oai_tools_menu.sh` abrirá um menu interativo com diversas opções para instalação, execução, logs e gerenciamento de componentes OAI. A execução de cada item ocorre em uma nova janela de terminal (ou sessão `tmux`, se sem ambiente gráfico).

### 🧩 Principais opções disponíveis:

| Nº    | Ação                                               |
| ----- | -------------------------------------------------- |
| 1     | Instalar Git, Docker e UHD                         |
| 2     | Instalar versões específicas da libuhd (4.4–4.7)   |
| 3     | Otimizações de performance (Intel/AMD)             |
| 4     | Instalar dependências do Core e RAN 5G             |
| 5     | Instalar dependências do EPC e RAN 4G              |
| 6     | Iniciar o Core 5G                                  |
| 7     | Iniciar o EPC 4G                                   |
| 8     | Visualizar logs do Core 5G (AMF)                   |
| 9     | Visualizar logs do EPC 4G (MME)                    |
| 10    | Parar o Core 5G                                    |
| 11    | Parar o EPC 4G                                     |
| 12–17 | Suporte a FlexRIC, near-RT RIC e xApps             |
| 18–24 | Inicialização de gNBs e eNBs (bare metal e docker) |

## ✅ Primeira execução (recomendado)

Para garantir que seu ambiente esteja pronto, execute as opções 1, 2 e 3 antes de usar os demais recursos:


```bash
1) Instalar Git, Docker e UHD
2) Instalar libuhd 4.4–4.7 📡
3) Modo performance 🚀
```
Essas opções preparam seu sistema com as dependências básicas necessárias para uso completo da suíte OAI.

## 📡 Iniciar 5GC ou EPC 4G

**5GC**: primeiramente devemos escolher a opção 4 do menu para instalar as dependências referentes ao CORE e RAN.

```bash
4) Dependências 5GC e RAN
```
Após concluir a instalação das dependências já podemos iniciar o 5GC com a opção 6. Os logs do AMF podem ser visualizados selecionando a opção 8. Para encerrar o 5GC selecione a opção 10.

```bash
6) Iniciar Core 5G
8) Logs Core 5G - AMF
10) Parar Core 5G
```

**4G**: primeiramente devemos escolher a opção 5 do menu para instalar as dependências referentes ao EPC e RAN.

```bash
4) Dependências EPC 4G e RAN
```
Após concluir a instalação das dependências já podemos iniciar o 4G EPC com a opção 7. Os logs do MME podem ser visualizados selecionando a opção 9. Para encerrar o EPC 4G selecione a opção 11.

```bash
7) Iniciar EPC 4G
9) Logs EPC 4G - MME
11) Parar EPC 4G
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