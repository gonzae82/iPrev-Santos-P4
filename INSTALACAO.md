# Guia de Instalação e Configuração do Sistema

Este guia descreve o passo a passo para instalar e executar a solução de monitoramento de custos do **IPREVSANTOS** que é composta por um banco de dados e um importador de dados via web (Streamlit).

O sistema utiliza Docker para garantir um ambiente consistente e de fácil configuração.

## 1. Componentes da Solução

A solução é composta por duas partes principais:
1.  **Banco de Dados MySQL (Docker):** Um banco de dados containerizado que armazena todos os dados de custos.
2.  **Importador de Dados (Streamlit):** Uma aplicação web (`app.py`) para carregar planilhas de dados, processá-las e inseri-las no banco de dados[cite: 25, 28].

## 2. Pré-requisitos

Antes de começar, garanta que os softwares abaixo estejam instalados e configurados em sua máquina.

### Windows
* **Docker Desktop:** Essencial para rodar os containers. Faça o download e instale a partir do [site oficial do Docker](https://www.docker.com/products/docker-desktop/).
  * Durante a instalação, certifique-se de que a opção de usar o backend **WSL 2** (Windows Subsystem for Linux 2) esteja habilitada.
* **Python:** Instale o Python 3.10 ou superior a partir do [site oficial do Python](https://www.python.org/downloads/windows/).
  * **Importante:** Durante a instalação, marque a caixa de seleção "Add Python to PATH".

### Linux (Ex: Debian/Ubuntu)
* **Docker Engine e Docker Compose:** Essenciais para rodar os containers. Siga o [guia de instalação oficial para o seu sistema](https://docs.docker.com/engine/install/ubuntu/).
  * **Importante (Pós-instalação):** Para evitar o uso de `sudo` em todos os comandos do Docker, adicione seu usuário ao grupo `docker`:
    ```bash
    sudo groupadd docker
    sudo usermod -aG docker $USER
    ```
    Depois, **faça logout e login novamente** na sua sessão para que a alteração tenha efeito.
* **Python:** Instale o Python 3.10+, pip e o módulo de ambiente virtual.
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    ```

## 3. Passos para Instalação e Execução

### Passo 3.1: Obter os Arquivos do Projeto

Clone ou faça o download deste projeto para a sua máquina e navegue até a pasta raiz pelo terminal.

```bash
cd caminho/para/projeto-iprevsantos
```

### Passo 3.2: Configurar o Ambiente Python

Dentro da pasta do projeto, crie e ative um ambiente virtual para instalar as dependências.

**No Windows (usando PowerShell ou CMD):**
```powershell
# Cria o ambiente virtual
python -m venv .venv

# Ativa o ambiente
.\.venv\Scripts\activate
```

**No Linux (ou macOS):**
```bash
# Cria o ambiente virtual
python3 -m venv .venv

# Ativa o ambiente
source .venv/bin/activate
```

Com o ambiente ativado, instale todas as bibliotecas necessárias com um único comando:
```bash
pip install -r requirements.txt
```

### Passo 3.3: Iniciar os Serviços (Banco de Dados e Aplicação)

Este comando irá construir as imagens Docker (na primeira vez) e iniciar todos os containers em segundo plano.

**No Windows (ou Linux, se o usuário foi adicionado ao grupo docker):**
```bash
docker compose up --build -d
```

**No Linux (se o usuário NÃO foi adicionado ao grupo docker):**
```bash
sudo docker compose up --build -d
```
*A opção `--build` só é necessária na primeira execução. Para as próximas vezes, `docker compose up -d` é suficiente.*

### Passo 3.4: Acessar os Componentes do Sistema

#### Acessando o Importador de Dados (Streamlit)
Abra seu navegador e acesse o seguinte endereço:
* **http://localhost:8501** Para importar os dados
* **http://localhost:8502** Para Prever os dados Futuros

#### Acessando o Banco de Dados Diretamente (MySQL)
Para depuração ou consultas manuais, você pode acessar o cliente MySQL diretamente no container.

1.  Abra um terminal na pasta do projeto e inicie uma sessão dentro do container do MySQL:

    **No Windows (ou Linux com usuário no grupo docker):**
    ```bash
    docker compose exec mysql-iprevsantos /bin/bash
    ```
    **No Linux (sem usuário no grupo docker):**
    ```bash
    sudo docker compose exec mysql-iprevsantos /bin/bash
    ```
2.  Dentro do terminal do container (o prompt mudará), conecte-se ao MySQL:
    ```bash
    mysql -u root -p
    ```
3.  O sistema pedirá a senha. Digite a senha definida no `docker-compose.yml` (ex: `iprev123`) e pressione Enter.
4.  Agora você está no console do MySQL e pode executar comandos SQL, como:
    ```sql
    USE iprev_dados;
    SELECT * FROM despesas ORDER BY id DESC LIMIT 5;
    exit;
    ```
    *Use `exit` duas vezes para sair do MySQL e depois do container.*

## 4. Como Desligar o Sistema

Para parar e remover todos os containers, execute o seguinte comando na pasta do projeto:

**No Windows (ou Linux com usuário no grupo docker):**
```bash
docker compose down
```

**No Linux (sem usuário no grupo docker):**
```bash
sudo docker compose down
```
*Para apagar também os dados do banco de dados, use `docker compose down -v`.*