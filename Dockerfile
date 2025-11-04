# 1. Imagem base: Usamos uma imagem oficial do Python na versão 3.10
FROM python:3.10-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copia o arquivo de dependências para o container
COPY requirements.txt .

# 4. Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia o script de inicialização
COPY ./config/start.sh /start.sh
RUN chmod +x /start.sh

# 6. Expõe a porta do Streamlit e do Jupyter
EXPOSE 8501
EXPOSE 8888

# 7. Comando padrão para iniciar a aplicação Streamlit quando o container for executado
#    --server.address=0.0.0.0 permite o acesso externo ao container
CMD ["/start.sh"]
