#!/bin/bash

## Author:   Paulo Eduardo da Silva Junior - paulo.eduardo.093@ufrn.edu.br - Tel: +55 (84) 9 8808-0933
## GitHub:   https://github.com/PauloBigooD
## Linkedin: https://www.linkedin.com/in/paulo-eduardo-5a18b3174/

set -e

## Variável de escolha de opção
COMMAND="$1"
## Work directory path is the current directory
WORK_DIR=$PWD
## Lista de versões disponíveis
VERSION_UHD=("UHD-4.7" "UHD-4.6" "UHD-4.5" "UHD-4.4" "UHD-4.3" "UHD-4.2" "UHD-4.1")
## Definindo o URL do repositório OAI - RAN
REPO_OAI_RAN="https://gitlab.eurecom.fr/oai/openairinterface5g.git"
## Versão da branch OAI - RAN
VERSION_RAN="2024.w42"
## Definindo o URL do repositório OAI - CORE
REPO_OAI_CORE="https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed.git"
## Versão da imagem Docker
DOCKER_IMAGE_OAI="v1.5.0"
## Interface de rede
INTERFACE_PC="enp3s"

DOCKER_CMD="docker compose"
[[ $# -eq 2 ]] && DOCKER_CMD="docker compose"

# Função para exibir ajuda
function show_help(){
    echo -e "Comandos comuns: 
            ------------------------------------------------------------------------------------
            ||   \e[0;34mOpções\e[0m        ||               🛠 \e[1;36m oai_tools \e[0m🛠                                ||
            |==================================================================================|
            || --install       || Instalar componentes Git, Docker e libuhd atualizados.      ||
            || --performance   || Instalar componentes Git e libuhd \e[1;33m4.4; 4.5; 4.6 ou 4.7\e[0m.     ||
            || --install_UHD   || Instalar modo performance para processador \e[1;31mAMD\e[0m ou \e[1;36mIntel\e[0m 🚀. ||
            || --install_5g    || Instalar dependências para Core e RAN 5G.                   ||
            || --install_4g    || Instalar dependências para EPC e RAN 4G.                    ||
            || --flexric       || Instalar dependências para FlexRIC                          ||
            || --start_5g      || Iniciar Core 5G.                                            ||
            || --start_4g      || Iniciar EPC 4G.                                             ||
            || --logs_5g       || Exibir logs Core 5G - AMF.                                  ||
            || --logs_4g       || Exibir logs EPC 4G - MME.                                   ||
            || --stop_5g       || Parar Core 5G.                                              ||
            || --stop_4g       || Parar EPC 4G.                                               ||
            |==================================================================================|
            |                             gNB's n310 in Docker 🐳                              |
            |==================================================================================|
            || --gNB_n106      || Iniciar gNB usrp 1 n310 5G - 106 prbs 📡                    ||
            || --gNB_n106_2    || Iniciar gNB usrp 2 n310 5G - 106 prbs 📡                    ||
            || --gNB_n162      || Iniciar gNB usrp 1 n310 5G - 162 prbs 📡                    ||
            || --gNB_n162_2    || Iniciar gNB usrp 2 n310 5G - 162 prbs 📡                    ||
            || --gNB_n273      || Iniciar gNB usrp 1 n310 5G - 273 prbs 📡                    ||
            || --gNB_n273_2    || Iniciar gNB usrp 2 n310 5G - 273 prbs 📡                    ||
            |==================================================================================|
            |                             gNB's n310 Bare Metal 🪖                              |
            |==================================================================================|
            || --gNB_n106_bm   || Iniciar gNB usrp 1 n310 5G - 106 prbs 📡                    ||
            || --gNB_n106_2_bm || Iniciar gNB usrp 2 n310 5G - 106 prbs 📡                    ||
            || --gNB_n162_bm   || Iniciar gNB usrp 1 n310 5G - 162 prbs 📡                    ||
            || --gNB_n162_2_bm || Iniciar gNB usrp 2 n310 5G - 162 prbs 📡                    ||
            || --gNB_n273_bm   || Iniciar gNB usrp 1 n310 5G - 273 prbs 📡                    ||
            || --gNB_n273_2_bm || Iniciar gNB usrp 2 n310 5G - 273 prbs 📡                    ||
            |==================================================================================|
            |                             gNB's b210 in Docker 🐳                              |
            |==================================================================================|
            || --gNB_b106      || Iniciar gNB usrp 1 b210 5G - 106 prbs 📡                    ||
            |==================================================================================|
            |                             gNB's b210 Bare Metal 🪖                              |
            |==================================================================================|
            || --gNB_b106_bm   || Iniciar gNB usrp 1 b210 5G - 106 prbs 📡                    ||
            |==================================================================================|
            |                             eNB's n310 in Docker 🐳                              |
            |==================================================================================|
            || --eNB_n100      || Iniciar eNB usrp 1 n310 4G - 100 prbs 📡                    ||
            || --eNB_n100_2    || Iniciar eNB usrp 2 n310 4G - 100 prbs 📡                    ||
            |==================================================================================|
            |                             eNB's n310 Bare Metal 🪖                              |
            |==================================================================================|
            || --eNB_n100_bm   || Iniciar gNB usrp 1 n310 5G - 100 prbs 📡                    ||
            || --eNB_n100_2_bm || Iniciar gNB usrp 2 n310 5G - 100 prbs 📡                    ||
            |==================================================================================|
    "
    }

# Função para verificar se um pacote está instalado
function is_installed(){
    dpkg -l | grep -q "$1"
    }
# Função para instalar pacotes se não estiverem instalados
function install_package() {
    for package in "$@"; do
        if ! is_installed "$package"; then
            echo "Instalando $package..."
            sudo apt-get install -y "$package"
        else
            echo "$package já está instalado."
        fi
    done
    }
# Função para gerenciar performance mode
function performance_mode(){
    install_package "linux-image-lowlatency" "linux-headers-lowlatency"
    if grep -m 1 'vendor_id' /proc/cpuinfo | grep -q 'GenuineIntel'; then
        echo "Intel CPU detectado. Configurando..."
        sudo sed -i '/^GRUB_CMDLINE_LINUX=/d' /etc/default/grub
        echo 'GRUB_CMDLINE_LINUX="quiet intel_pstate=disable processor.max_cstate=1 intel_idle.max_cstate=0"' | sudo tee -a /etc/default/grub
        echo 'blacklist intel_powerclamp' | sudo tee -a /etc/modprobe.d/blacklist.conf
        echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
        sudo update-grub
        install_package "i7z"
        install_package "cpufrequtils"
        sudo systemctl restart cpufrequtils
    elif grep -m 1 'vendor_id' /proc/cpuinfo | grep -q 'AuthenticAMD'; then
        echo "AMD CPU detectado. Configurando..."
        sudo sed -i '/^GRUB_CMDLINE_LINUX=/d' /etc/default/grub
        echo 'GRUB_CMDLINE_LINUX="quiet amd_pstate=disable processor.max_cstate=1 idle=nomwait processor.max_cstate=0"' | sudo tee -a /etc/default/grub
        echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
        sudo update-grub
        install_package "cpufrequtils"
        sudo systemctl restart cpufrequtils
    else
        echo "CPU não identificada."
    fi
    }
# Função para verificar dispositivos USRP
function check_usrp_device(){
    echo "Realizando a verificação da USRP"
    uhd_find_devices 2>&1 | {
    skip=1  # Variável para controlar a primeira linha
    output=""

    while read -r line; do
        if [ $skip -eq 1 ]; then
            skip=0  # Ignora a primeira linha
            continue
        fi
        if echo "$line" | grep -q "No UHD Devices Found"; then
            echo "Verifique se a USRP encontra-se conectada a uma porta USB 3.0"
        fi
    done
    }
    uhd_find_devices
    echo "--------------------------------------------------"
    }
# Função que verifica acionamento da dashboard OAI
function dashboard_check(){
    # Condição que verifica o uso da Dashboard
    if [ "$2" = "-d" ];then
        dash="$2"
        echo -e "Dashboard \e[92mON\e[0m"
    elif [[ "$2" == -* ]];then
        dash=" "
        echo -e "Parâmetro inválido, este deve ser igual a \e[33m-d\e[0m"
    else
        dash=" "
        echo -e "Dashboard \e[31mOFF\e[0m"
    fi
    }
# Função que instala o modo performance
function init_performance(){
    ## Performance mode
	sudo /etc/init.d/cpufrequtils restart
    ## Configuration of the packer forwarding
	sudo sysctl net.ipv4.conf.all.forwarding=1
	sudo iptables -P FORWARD ACCEPT
    }

# Função para compilar e instalar UHD
function install_libuhd() {
    # Verifica se a UHD já está instalada
    if command -v uhd_find_devices &> /dev/null; then
        echo "A biblioteca UHD já está instalada."
        read -p "Deseja reinstalá-la? (s/n): " resposta
        case "$resposta" in
            [Ss]* )
                echo "Reinstalando a biblioteca UHD..."
                ;;
            [Nn]* )
                echo "Nenhuma ação será realizada."
                return 0
                ;;
            * )
                echo "Resposta inválida. Nenhuma ação será realizada."
                return 1
                ;;
        esac
    fi
    echo "Removendo instalações anteriores..."
    sudo rm -rf /usr/local/lib/cmake/uhd
    sudo rm -rf /usr/local/share/doc/uhd
    sudo rm -rf /usr/share/uhd
    sudo rm -rf /usr/share/doc/uhd
    sudo rm -rf /usr/lib/cmake/uhd
    sudo rm -rf ./uhd
    sudo rm -rf /usr/local/lib/uhd
    sudo rm -rf /usr/local/include/uhd
    sudo rm -rf /usr/local/share/uhd

    echo "Escolha a versão da UHD para instalar:"
    for i in "${!VERSION_UHD[@]}"; do
        echo "$((i+1)). ${VERSION_UHD[i]}"
    done
    read -p "Digite o número correspondente à versão desejada: " escolha
    if [[ "$escolha" -ge 1 && "$escolha" -le "${#VERSION_UHD[@]}" ]]; then
        VERSAO_SELECIONADA="${VERSION_UHD[$((escolha-1))]}"
    else
        echo "Escolha inválida. Tente novamente."
        escolher_versao
    fi
    echo "Instalando dependências..."
    sudo apt-get update
    install_package "autoconf " "automake" "ccache" "build-essential" "cmake" "doxygen" "ethtool" "g++" "inetutils-tools" "libboost-all-dev" "libncurses5" "libncurses5-dev" "libusb-1.0-0" "libusb-1.0-0-dev" "libusb-dev" "python3-dev" "python3-mako" "python3-numpy" "python3-requests" "python3-scipy" "python3-setuptools" "python3-ruamel.yaml"
    echo "Instalando UHD versão: $VERSAO_SELECIONADA"
    git clone --branch "$VERSAO_SELECIONADA" https://github.com/EttusResearch/uhd.git
    cd uhd/host || exit
    mkdir build
    cd build || exit
    cmake ../
    make -j"$(nproc)"
    sudo make install
    sudo ldconfig
    # Verificação da instalação
    echo "Verificando a instalação..."
    uhd_find_devices
    uhd_usrp_probe
    }

# Função que instala o Docker
function install_docker(){
    if is_installed docker; then
        echo "Docker já instalado."
    else
        echo "Instalando Docker..."
        # Instalar dependências comuns
        install_package "apt-transport-https" "ca-certificates" "curl" "gnupg" "lsb-release" "python3-pip"
        # Criar o diretório para armazenar a chave GPG, caso não exista
        sudo mkdir -p /etc/apt/keyrings
        # Adicionar chave GPG do Docker
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc
        sudo gpg --no-default-keyring --keyring /etc/apt/keyrings/docker.gpg --import /etc/apt/keyrings/docker.asc
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
        # Detectar a distribuição do sistema
        DISTRO=$(lsb_release -si)
        CODENAME=$(lsb_release -cs)
        if [[ "$DISTRO" == "Ubuntu" ]]; then
            echo "Distribuição Ubuntu detectada."
            echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/ubuntu $CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        elif [[ "$DISTRO" == "Debian" ]]; then
            echo "Distribuição Debian detectada."
            echo "deb [arch=$(dpkg --print-architecture)] https://download.docker.com/linux/debian $CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        elif [[ "$DISTRO" == "CentOS" || "$DISTRO" == "RHEL" || "$DISTRO" == "Fedora" ]]; then
            echo "Distribuição baseada em RedHat detectada."
            # Para distribuições como CentOS/RHEL/Fedora, usamos repositórios diferentes
            curl -fsSL https://download.docker.com/linux/centos/docker-ce.repo | sudo tee /etc/yum.repos.d/docker-ce.repo > /dev/null
        else
            echo "Distribuição não suportada para instalação automatizada."
            exit 1
        fi
        # Atualizar repositórios e instalar Docker
        sudo apt-get update
        install_package "docker-ce" "docker-ce-cli" "containerd.io" "docker-buildx-plugin" "docker-compose-plugin"
        # Instalar Docker Compose via pip3 (opcional, se não instalado com o plugin)
        sudo pip3 install docker-compose
    fi
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-get clean
    }
# Função que clona o repositorio da RAN do oai
function clone_repo_RAN(){
    cd $WORK_DIR || exit
    if [ -d "openairinterface5g" ]; then
        echo "Removendo diretório existente 'openairinterface5g'..."
        sudo rm -rf openairinterface5g
    fi
    if [ ! -d "openairinterface5g" ]; then
        echo "Clone OpenAirInterface 4G/5G RAN repository"
        git clone "$REPO_OAI_RAN"
        cd openairinterface5g || exit
        git checkout $VERSION_RAN
    else
        echo "Erro: Não foi possível remover o diretório."
    fi
    }

# Função que clona repositorio do CORE do 
function clone_REPO_OAI_CORE(){
    if [ -d "oai-cn5g-fed" ]; then
        echo "Removendo o diretório existente ' oai-cn5g-fed'..."
        sudo rm -rf  oai-cn5g-fed
    fi
    if [ ! -d "oai-cn5g-fed" ]; then
        echo "Clone OpenAirInterface 5G Core repository"
        git clone "$REPO_OAI_CORE"
        cd oai-cn5g-fed || exit
        git checkout -f $DOCKER_IMAGE_OAI
    else
        echo "Erro: Não foi possível remover o diretório."
    fi
    }

# Função para configurar e compilar a RAN do OpenAirInterface
function build_oai_RAN(){
    echo "Install OAI dependencies and Build OAI RAN"
    cd $WORK_DIR || exit
    cd openairinterface5g || exit
    source oaienv
    cd cmake_targets || exit
    sudo ./build_oai -I
    sudo ./build_oai -I --install-optional-packages
    sudo ./build_oai -w USRP --ninja --build-e2 --gNB --eNB --nrUE -C --build-lib "uescope nrscope enbscope telnetsrv"
    }

# Função que realiza o deploy da RAN e EPC do OAI
function start_4g(){
    stop_4g
    sudo sysctl net.ipv4.conf.all.forwarding=1
    sudo iptables -P FORWARD ACCEPT
    sudo sysctl -w net.core.wmem_max=33554432
    sudo sysctl -w net.core.rmem_max=33554432
    sudo sysctl -w net.core.wmem_default=33554432
    sudo sysctl -w net.core.rmem_default=33554432
    echo "Deploy and Configure Cassandra Database"
    cd $WORK_DIR/core-scripts || exit
    ## Un-deployment olds containers
    sudo docker compose down
    ## Deploy and Configure Cassandra Database
    sudo docker compose -f docker-compose-4g.yml up -d db_init
    ## Run docker COMMAND in background
    sudo docker logs rfsim4g-db-init --follow &
    ## Monitor docker COMMAND output
    while :
    do
    ## Checks if the COMMAND output contains "OK"
    if sudo docker logs rfsim4g-db-init | grep -q "OK"; then
        echo "Status OK!"
        sudo docker rm rfsim4g-db-init
        ## Deploy Magma-MME
        sleep 5
        sudo docker compose -f docker-compose-4g.yml up -d magma_mme oai_spgwu trf_gen
        ## Container list
	sleep 5
        sudo docker compose ps -a
	break
	fi
	sleep 20
	done
    }

# Função que realiza o deploy da RAN e CORE do OAI
function start_5g(){
    stop_5g
    sudo sysctl net.ipv4.conf.all.forwarding=1
    sudo iptables -P FORWARD ACCEPT
    sudo sysctl -w net.core.wmem_max=33554432
    sudo sysctl -w net.core.rmem_max=33554432
    sudo sysctl -w net.core.wmem_default=33554432
    sudo sysctl -w net.core.rmem_default=33554432
    cd $WORK_DIR/core-scripts || exit
    sudo python3 core-network.py --type start-basic --scenario 1
    sleep 20
    docker ps -a
    }

# Função para realizar pull imagens docker 4G
function pull_docker_4g(){
    echo "Pulling the images from Docker Hub"
    sudo docker pull cassandra:2.1
    sudo docker pull redis:6.0.5
    sudo docker pull oaisoftwarealliance/oai-hss:latest
    sudo docker pull oaisoftwarealliance/magma-mme:latest
    sudo docker pull oaisoftwarealliance/oai-spgwc:latest
    sudo docker pull oaisoftwarealliance/oai-spgwu-tiny:latest
    sudo docker pull oaisoftwarealliance/oai-enb:develop
    sudo docker pull oaisoftwarealliance/oai-lte-ue:develop
    ## Re-tag
    sudo docker image tag oaisoftwarealliance/oai-spgwc:latest oai-spgwc:latest
    sudo docker image tag oaisoftwarealliance/oai-hss:latest oai-hss:latest
    sudo docker image tag oaisoftwarealliance/oai-spgwu-tiny:latest oai-spgwu-tiny:latest
    sudo docker image tag oaisoftwarealliance/magma-mme:latest magma-mme:latest
    }
# Função para realizar pull imagens docker 5G
function pull_docker_5g(){
    echo "Pulling the images from Docker Hub"   
    ## Pulling the images from Docker Hub
    sudo docker pull oaisoftwarealliance/oai-amf:$DOCKER_IMAGE_OAI
    sudo docker pull oaisoftwarealliance/oai-nrf:$DOCKER_IMAGE_OAI
    sudo docker pull oaisoftwarealliance/oai-smf:$DOCKER_IMAGE_OAI
    sudo docker pull oaisoftwarealliance/oai-udr:$DOCKER_IMAGE_OAI
    sudo docker pull oaisoftwarealliance/oai-udm:$DOCKER_IMAGE_OAI
    sudo docker pull oaisoftwarealliance/oai-ausf:$DOCKER_IMAGE_OAI
    sudo docker pull oaisoftwarealliance/oai-spgwu-tiny:$DOCKER_IMAGE_OAI
    sudo docker pull oaisoftwarealliance/trf-gen-cn5g:latest
    ## Tag Docker Images
    sudo docker image tag oaisoftwarealliance/trf-gen-cn5g:latest trf-gen-cn5g:latest
    sudo docker image tag oaisoftwarealliance/oai-amf:$DOCKER_IMAGE_OAI oai-amf:$DOCKER_IMAGE_OAI
    sudo docker image tag oaisoftwarealliance/oai-nrf:$DOCKER_IMAGE_OAI oai-nrf:$DOCKER_IMAGE_OAI
    sudo docker image tag oaisoftwarealliance/oai-smf:$DOCKER_IMAGE_OAI oai-smf:$DOCKER_IMAGE_OAI
    sudo docker image tag oaisoftwarealliance/oai-udr:$DOCKER_IMAGE_OAI oai-udr:$DOCKER_IMAGE_OAI
    sudo docker image tag oaisoftwarealliance/oai-udm:$DOCKER_IMAGE_OAI oai-udm:$DOCKER_IMAGE_OAI
    sudo docker image tag oaisoftwarealliance/oai-ausf:$DOCKER_IMAGE_OAI oai-ausf:$DOCKER_IMAGE_OAI
    sudo docker image tag oaisoftwarealliance/oai-spgwu-tiny:$DOCKER_IMAGE_OAI oai-spgwu-tiny:$DOCKER_IMAGE_OAI
    }

# Função que pausa o 4G OAI
function stop_4g(){
    ## 4G EPC stop
    cd $WORK_DIR/core-scripts || exit
    sudo docker compose down
    }

# Função que pausa o 5G OAI
function stop_5g(){
    cd $WORK_DIR/core-scripts
    sudo docker rm -f rfsim5g-oai-gnb
    sudo python3 core-network.py --type stop-basic
    }

# Função que gera o log do MME 4G OAI
function logs_4g() {
    ## Verifica se o contêiner EPC está em execução
    if sudo docker inspect -f '{{.State.Running}}' rfsim4g-magma-mme | grep true > /dev/null; then
        ## Exibe os logs do EPC
        echo "Exibindo logs do 4G EPC..."
        sudo docker exec -it rfsim4g-magma-mme /bin/bash -c "tail -f /var/log/mme.log"
    else
        ## Exibe mensagem se o EPC não estiver em execução
        echo "O EPC não está em execução. Por favor, selecione a opção 7 do menu para iniciar o EPC 4G."
    fi
    }

# Função que gera o log do AMF 5G OAI
function logs_5g() {
    ## Verifica se o contêiner 5G Core está em execução
    if sudo docker inspect -f '{{.State.Running}}' oai-amf | grep true > /dev/null; then
        ## Exibe os logs do 5G Core
        echo "Exibindo logs do 5G Core..."
        sudo docker logs -f oai-amf
    else
        ## Exibe mensagem se o 5G Core não estiver em execução
        echo "O 5G Core não está em execução. Por favor, selecione a opção 6 do menu para iniciar o Core 5G."
    fi
    }

# Função para checar mcc, mnc e IP do arquivo de configuração da eNB
function chek_eNB_conf(){
    sudo docker rm -f oai-enb oai-enb-2
    # check_usrp_device
    if [ "$4" = "docker" ]; then
        cd $WORK_DIR || exit
        ${DOCKER_CMD} -f docker-compose/docker-compose-"$1""$2"-PRB"$3""$5".yaml up
    else
        dashboard_check
	cd $WORK_DIR || exit
        # Caminho do arquivo de configuração
        CONFIG_FILE="conf/${1}${2}PRB${3}bm${5}.conf"
        # Verifica se o arquivo existe
        if [ ! -f "$CONFIG_FILE" ]; then
            echo "Arquivo de configuração não encontrado: $CONFIG_FILE"
            exit 1
        fi
        # Novos valores
        NEW_MCC=208
        NEW_MNC=96
        NEW_MME_IP=192.168.61.3
        # Inicializa a variável de IP
        IP_ADDRESS=""
        # Laço para verificar as interfaces enp3s0 até enp3s4
        for i in {0..4}; do
            INTERFACE="enp3s$i"
            IP_ADDRESS=$(ip -4 addr show "$INTERFACE" 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
            if [ -n "$IP_ADDRESS" ]; then
                break
            fi
        done
        # Verifica se um endereço IP foi encontrado
        if [ -z "$IP_ADDRESS" ]; then
            echo "Nenhum endereço IP encontrado para as interfaces enp3s0 a enp3s4"
            exit 1
        fi
        # Faz as substituições no arquivo de configuração
        sed -i.bak \
            -e "s/mcc = [0-9]\{3\};/mcc = $NEW_MCC;/" \
            -e "s/mnc = [0-9]\{2\};/mnc = $NEW_MNC;/" \
            -e "s/ENB_IPV4_ADDRESS_FOR_S1_MME *= *\"[0-9.]*\";/ENB_IPV4_ADDRESS_FOR_S1_MME              = \"$IP_ADDRESS\";/" \
            -e "s/ENB_IPV4_ADDRESS_FOR_S1U *= *\"[0-9.]*\";/ENB_IPV4_ADDRESS_FOR_S1U                 = \"$IP_ADDRESS\";/" \
            -e "s/ENB_IPV4_ADDRESS_FOR_X2C *= *\"[0-9.]*\";/ENB_IPV4_ADDRESS_FOR_X2C                 = \"$IP_ADDRESS\";/" \
            -e "s/mme_ip_address = ({ ipv4 = \"[0-9.]*\";/mme_ip_address = ({ ipv4 = \"$NEW_MME_IP\";/" \
            -e "s/ENB_INTERFACE_NAME_FOR_S1_MME *= *\"[^\"]*\";/ENB_INTERFACE_NAME_FOR_S1_MME            = \"$INTERFACE\";/" \
            -e "s/ENB_INTERFACE_NAME_FOR_S1U *= *\"[^\"]*\";/ENB_INTERFACE_NAME_FOR_S1U               = \"$INTERFACE\";/" \
            "$CONFIG_FILE"
        # Exibe uma mensagem de sucesso
        echo "Configurações atualizadas com sucesso no arquivo: $CONFIG_FILE"
        cd openairinterface5g/cmake_targets/ran_build/build/
	sudo -E ./lte-softmodem -O ../../../../conf/${1}${2}PRB${3}bm${5}.conf $dash
    fi
    }

# Função para checar mcc, mnc e IP do arquivo de configuração da gNB
function chek_gNB_conf(){
    sudo docker rm -f rfsim5g-oai-gnb
    sudo docker rm -f oai-gnb oai-gnb-2 
    #check_usrp_device
    if [ "$4" = "docker" ]; then
        cd "$WORK_DIR" || exit
        ${DOCKER_CMD} -f docker-compose/docker-compose-"$1""$2"-PRB"$3""$5".yaml up
    else
        dashboard_check
        # Caminho do arquivo de configuração
        CONFIG_FILE="conf/${1}${2}PRB${3}bm${5}.conf"             
        # Inicializa a variável de IP
        IP_ADDRESS=""        
        # Novos valores
        NEW_MCC=001
        NEW_MNC=01
        NEW_TRACKING_AREA_CODE=0x0001
        NEW_AMF_IP="192.168.70.132"
        NEW_SNSSAI="snssaiList = ({ sst = 1; sd = 0x1 });"
        # Laço para verificar as interfaces enp3s0 até enp3s4
        for i in {0..4}; do
            INTERFACE="$INTERFACE_PC$i"
            IP_ADDRESS=$(ip -4 addr show "$INTERFACE" 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
            if [ -n "$IP_ADDRESS" ]; then
                break
            fi
        done
        # Verifica se um endereço IP foi encontrado
        if [ -z "$IP_ADDRESS" ]; then
            echo "Nenhum endereço IP encontrado para as interfaces $INTERFACE_PC a enp3s4"
            exit 1
        fi
        # Faz as substituições no arquivo de configuração
        sed -i.bak \
            -e "s/mcc = [0-9]\{3\};/mcc = $NEW_MCC;/" \
            -e "s/mnc = [0-9]\{2\};/mnc = $NEW_MNC;/" \
            -e "s/tracking_area_code = [0-9a-fx]*;/tracking_area_code = $NEW_TRACKING_AREA_CODE;/" \
            -e "s/snssaiList = ({ sst = 1; sd = [0-9a-fx]* });/$NEW_SNSSAI/" \
            -e "s/amf_ip_address = ({ ipv4 = \"[0-9.]*\";/amf_ip_address = ({ ipv4 = \"$NEW_AMF_IP\";/" \
            -e "s/GNB_IPV4_ADDRESS_FOR_NG_AMF *= *\"[0-9.\/]*\";/GNB_IPV4_ADDRESS_FOR_NG_AMF = \"$IP_ADDRESS\";/" \
            -e "s/GNB_IPV4_ADDRESS_FOR_NGU *= *\"[0-9.\/]*\";/GNB_IPV4_ADDRESS_FOR_NGU = \"$IP_ADDRESS\";/" \
            -e "s/GNB_INTERFACE_NAME_FOR_NG_AMF *= *\"[^\"]*\";/GNB_INTERFACE_NAME_FOR_NG_AMF = \"$INTERFACE\";/" \
            -e "s/GNB_INTERFACE_NAME_FOR_NGU *= *\"[^\"]*\";/GNB_INTERFACE_NAME_FOR_NGU = \"$INTERFACE\";/" \
        "$CONFIG_FILE"
        # Exibe uma mensagem de sucesso
        echo "Configurações atualizadas com sucesso no arquivo: $CONFIG_FILE"
        cd openairinterface5g/cmake_targets/ran_build/build/
        # Iniciar o softmodem
        sudo RFSIMULATOR=server ./nr-softmodem --rfsim --sa -O ../../../../conf/${1}${2}PRB${3}bm${5}.conf --gNBs.[0].min_rxtxtime 6 --continuous-tx $dash
    fi
    }

function start_nearRT-RIC(){
    cd flexric
    ./build/examples/ric/nearRT-RIC
    }

function start_E2Agent(){
    cd flexric
    ./build/examples/emulator/agent/emu_agent_gnb
    }

function start_gNB_rfsim(){
    # Caminho do arquivo de configuração
    CONFIG_FILE="openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf"                
    NEW_MCC=001
    NEW_MNC=01
    NEW_TRACKING_AREA_CODE=0x0001
    NEW_AMF_IP="192.168.70.132"
    NEW_SNSSAI="snssaiList = ({ sst = 1; sd = 0x1 });"
    # Faz as substituições no arquivo de configuração
    sed -i.bak \
        -e "s/mcc = [0-9]\{3\};/mcc = $NEW_MCC;/" \
        -e "s/mnc = [0-9]\{2\};/mnc = $NEW_MNC;/" \
        -e "s/tracking_area_code = [0-9a-fx]*;/tracking_area_code = $NEW_TRACKING_AREA_CODE;/" \
        -e "s/snssaiList = ({ sst = 1; sd = [0-9a-fx]* });/$NEW_SNSSAI/" \
        -e "s/amf_ip_address = ({ ipv4 = \"[0-9.]*\";/amf_ip_address = ({ ipv4 = \"$NEW_AMF_IP\";/" \
    "$CONFIG_FILE"
    # Exibe uma mensagem de sucesso
    echo "Configurações atualizadas com sucesso no arquivo: $CONFIG_FILE"
    cd openairinterface5g/cmake_targets/ran_build/build/
    # Iniciar o softmodem
    sudo ./nr-softmodem --rfsimulator server --rfsim --sa -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/gnb.sa.band78.fr1.106PRB.usrpb210.conf --continuous-tx --gNBs.[0].min_rxtxtime 6
    }

function start_UE_rfsim(){
    CONFIG_FILE="openairinterface5g/targets/PROJECTS/GENERIC-NR-5GC/CONF/ue.conf"
    NEW_imsi="001010000000003"
    NEW_key="fec86ba6eb707ed08905757b1bb44b8f"
    NEW_opc="C42449363BBAD02B66D16BC975D77CC1"
    NEW_dnn="oai"
    NEW_nssai_sst=1
    NEW_nssai_sd=1
    sed -i.bak \
        -e "s/imsi *= *\"[^\"]*\";/imsi = \"$NEW_imsi\";/" \
        -e "s/key *= *\"[^\"]*\";/key = \"$NEW_key\";/" \
        -e "s/opc *= *\"[^\"]*\";/opc = \"$NEW_opc\";/" \
        -e "s/dnn *= *\"[^\"]*\";/dnn = \"$NEW_dnn\";/" \
        -e "s/nssai_sst *= *[0-9]*;/nssai_sst = $NEW_nssai_sst;/" \
        -e "s/nssai_sd *= *[0-9]*;/nssai_sd = $NEW_nssai_sd;/" \
        "$CONFIG_FILE"
    echo "Configurações atualizadas com sucesso no arquivo: $CONFIG_FILE"  
    cd openairinterface5g/cmake_targets/ran_build/build/
    sudo ./nr-uesoftmodem --rfsimulator.serveraddr 192.168.70.129 -r 106 --numerology 1 --band 78 -C 3619200000 --rfsim --sa -O ../../../targets/PROJECTS/GENERIC-NR-5GC/CONF/ue.conf
    }

function FlexRIC() {
    echo "Instalando dependências do FlexRIC"
    sudo apt-get update
    install_package "automake" "g++" "make" "libpcre2-dev" "byacc" "cmake" "python3-dev" "libsctp-dev" "bison" 
    cd $WORK_DIR || exit
    if [ -d "swig" ]; then
        echo "Removendo diretório existente 'swig'..."
        sudo rm -rf swig
    fi
    if [ ! -d "swig" ]; then
    echo "Instalando SWIG"
    git clone https://github.com/swig/swig.git
    cd "$WORK_DIR"/swig || { echo "Erro ao acessar o diretório swig"; exit 1; }
    git checkout release-4.1
    ./autogen.sh || { echo "Erro no autogen.sh do SWIG"; exit 1; }
    ./configure --prefix=/usr/ || { echo "Erro na configuração do SWIG"; exit 1; }
    make -j8 || { echo "Erro ao compilar SWIG"; exit 1; }
    sudo make install || { echo "Erro ao instalar SWIG"; exit 1; }
    cd $WORK_DIR || exit
    else
        echo "Erro: Não foi possível remover o diretório."
    fi
    if [ -d "flexric" ]; then
        echo "Removendo diretório existente 'flexric'..."
        sudo rm -rf flexric
    fi
    if [ ! -d "flexric" ]; then
    echo "Instalando FlexRIC"
    cd "$WORK_DIR" || { echo "Erro ao acessar WORK_DIR"; exit 1; }
    git clone https://gitlab.eurecom.fr/mosaic5g/flexric.git
    cd flexric || { echo "Erro ao acessar diretório flexric"; exit 1; }
    git checkout dev #  beabdd072ca9e381d4d27c9fbc6bb19382817489|| { echo "Erro ao alternar para o branch dev"; exit 1; }
    mkdir -p build
    cd build || { echo "Erro ao acessar diretório build"; exit 1; }
    cmake .. || { echo "Erro no comando cmake"; exit 1; }
    make -j8 || { echo "Erro ao compilar FlexRIC"; exit 1; }
    sudo make install || { echo "Erro ao instalar FlexRIC"; exit 1; }
    #ctest -j8 --output-on-failure
    else
        echo "Erro: Não foi possível remover o diretório."
    fi
    if type clone_repo_RAN >/dev/null 2>&1; then
        clone_repo_RAN
    else
        echo "Função clone_repo_RAN não encontrada. Certifique-se de que está definida."
    fi
    # Chamada para build_oai_RAN (necessário definir antes de usar)
    if type build_oai_RAN >/dev/null 2>&1; then
        build_oai_RAN
    else
        echo "Função build_oai_RAN não encontrada. Certifique-se de que está definida."
    fi
    }

function xApps(){
    while true; do
        echo -e "
        --------------------------------------------------------------------------------------------------------------------------------------------------
        | 1 - xapp_kpm_moni               <-> Start the KPM monitor xApp - measurements stated in 2.1.1 E2SM-KPM.                                        |
        | 2 - xapp_rc_moni                <-> Start the RC monitor xApp - aperiodic subscription for UE RRC State Change.                                |
        | 3 - xapp_kpm_rc                 <-> Start the RC control xApp - RAN control function QoS flow mapping configuration (e.g. creating a new DRB). |
        | 4 - xapp_gtp_mac_rlc_pdcp_moni  <-> Start the (MAC + RLC + PDCP + GTP) monitor xApp.                                                           |
        --------------------------------------------------------------------------------------------------------------------------------------------------
        "
    read -p "Escolha uma opção [1 ... 4] para deploy: " escolha
    case $escolha in
        1) ./flexric/build/examples/xApp/c/monitor/xapp_kpm_moni ;;
        2) ./flexric/build/examples/xApp/c/monitor/xapp_rc_moni ;;
        3) ./flexric/build/examples/xApp/c/kpm_rc/xapp_kpm_rc ;;
        4) ./flexric/build/examples/xApp/c/monitor/xapp_gtp_mac_rlc_pdcp_moni ;;
        *) echo "Opção inválida! Tente novamente." ;;
        esac
        echo ""
    done    
    }

# Case principal
case "${COMMAND}" in
    "--help")
        show_help
        ;;
    "--install")
        install_package "git"
        install_docker
        install_libuhd
        ;;
    "--performance")
        performance_mode
        ;;
    "--install_UHD")
        install_package "git"
        install_libuhd
        ;;
    "--install_4g")
        clone_repo_RAN
        build_oai_RAN
        pull_docker_4g
        ;;
    "--start_4g")
        init_performance
        start_4g
        ;;
    "--stop_4g")
        stop_4g
        ;;
    "--logs_4g")
        logs_4g
        ;;
    "--install_5g")
        clone_repo_RAN
        build_oai_RAN
        pull_docker_5g
        ;;
    "--start_5g")
        init_performance
        start_5g
        ;;
    "--stop_5g")
        stop_5g
        ;;
    "--logs_5g")
        logs_5g
        ;;
    "--eNB_n100")
        chek_eNB_conf "n" "310" "100" "docker" ""
        ;;
    "--eNB_n100_bm")
        chek_eNB_conf "n" "310" "100" "" ""
        ;;
    "--eNB_n100_2")
        chek_eNB_conf "n" "310" "100" "docker" "_2"
        ;;
    "--eNB_n100_2_bm")
        chek_eNB_conf "n" "310" "100" "" "_2"
        ;;
    "--gNB_n106")
        chek_gNB_conf "n" "310" "106" "docker" ""
        ;;
    "--gNB_n106_2")
        chek_gNB_conf "n" "310" "106" "docker" "_2"
        ;;
    "--gNB_n106_bm")
        chek_gNB_conf "n" "310" "106" "" ""
        ;;
    "--gNB_n106_2_bm")
        chek_gNB_conf "n" "310" "106" "" "_2"
        ;;
    "--gNB_n162")
        chek_gNB_conf "n" "310" "162" "docker" ""
        ;;
    "--gNB_n162_2")
        chek_gNB_conf "n" "310" "162" "docker" "_2"
        ;;
    "--gNB_n162_2_bm")
        chek_gNB_conf "n" "310" "162" "" "_2"
        ;;
    "--gNB_n162_bm")
        chek_gNB_conf "n" "310" "162" "" ""
        ;;
    "--gNB_n273")
        chek_gNB_conf "n" "310" "273" "docker" ""
        ;;
    "--gNB_n273_2")
        chek_gNB_conf "n" "310" "273" "docker" "_2"
        ;;
    "--gNB_n273_bm")
        chek_gNB_conf "n" "310" "273" "" ""
        ;;
    "--gNB_n273_2_bm")
        chek_gNB_conf "n" "310" "273" "" "_2"
        ;;
    "--gNB_b106")
        chek_gNB_conf "b" "210" "106" "docker" ""      
        ;;
    "--gNB_b106_bm")
        chek_gNB_conf "b" "210" "106" "" ""      
        ;;
    "--FlexRIC")
        FlexRIC
        ;;
    "--start_nearRT-RIC")
        start_nearRT-RIC
        ;;
    "--start_E2Agent")
        start_E2Agent
        ;;
    "--start_gNB_rfsim")
        start_gNB_rfsim
        ;;
    "--start_UE_rfsim")
        start_UE_rfsim
        ;;
    "--xApps")
        xApps
        ;;
        *)
echo " COMMAND not Found."
show_help
exit 127;
;;
esac
