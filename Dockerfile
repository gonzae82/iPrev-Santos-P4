# 1. Imagem base: Usamos uma imagem oficial do Python na versão 3.10
FROM python:3.10-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copia o arquivo de dependências para o container
COPY requirements.txt .

# 4. Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia todos os outros arquivos do projeto (app.py, notebook, etc.) para o container
COPY . .

# 6. Expõe a porta do Streamlit e do Jupyter
EXPOSE 8501
EXPOSE 8888

# 7. Comando padrão para iniciar a aplicação Streamlit quando o container for executado
#    --server.address=0.0.0.0 permite o acesso externo ao container
CMD ["streamlit", "run", "app/importar_dados.py", "--server.port=8501", "--server.address=0.0.0.0"]