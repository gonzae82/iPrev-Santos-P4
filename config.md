# Projeto Integrador: Monitoramento de Custos - IPREVSANTOS

Este projeto implementa uma solução tecnológica para o monitoramento e análise de custos no Instituto de Previdência dos Servidores Públicos Municipais de Santos (IPREVSANTOS), conforme proposto no Relatório Técnico-Científico da disciplina de Projeto Integrador IV.

##  Solução

A solução é composta por três partes principais:
1.  **Banco de Dados MySQL (Docker):** Um banco de dados containerizado que armazena todos os dados de custos.
2.  **Importador de Dados (Streamlit):** Uma aplicação web (`app.py`) para carregar planilhas de dados, processá-las e inseri-las no banco de dados.
3.  **Análise Preditiva (Meta Prophet):** Um notebook (`predicao_custos.py`) para análise exploratória e desenvolvimento de um modelo preditivo de custos.

## Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados em sua máquina:
* [Docker](https://www.docker.com/get-started) e Docker Compose
* [Python 3.10+](https://www.python.org/downloads/) e `pip`

## Instruções de Instalação e Execução

Siga os passos abaixo para configurar e executar o projeto.

### 1. Preparar o Ambiente

Clone ou faça o download deste projeto para a sua máquina e navegue até a pasta raiz pelo terminal.

```bash
cd caminho/para/projeto-iprevsantos
```

Crie um ambiente virtual (recomendado) e ative-o:
```bash
# Para Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Para Windows
python -m venv .venv
.venv\Scripts\activate
```

Instale todas as dependências do Python:
```bash
pip install -r requirements.txt
```

### 2. Iniciar o Banco de Dados

Com o Docker em execução na sua máquina, inicie o container do MySQL em segundo plano.
```bash
sudo docker compose up -d
```
*Este comando irá criar e iniciar o banco de dados. Na primeira vez, ele executará o script `init.sql` para criar a tabela `despesas`.*

### 3. Executar o Importador de Dados

Para carregar novos dados, inicie a aplicação Streamlit:
```bash
streamlit run app.py
```
*A aplicação será aberta automaticamente no seu navegador. Use a interface para selecionar e importar suas planilhas.*

### 4. Executar a Análise Preditiva

Para trabalhar na análise e no modelo preditivo, inicie o Jupyter Notebook:
```bash
jupyter notebook notebook_analise.ipynb
```
*Isso abrirá o notebook no seu navegador, onde você poderá executar as células de código para análise e modelagem.*

## Para Desligar

Para parar o container do banco de dados, execute na pasta do projeto:
```bash
sudo docker compose down
```