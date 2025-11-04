#!/bin/bash

# Executa o Streamlit em background
streamlit run app/importar_dados.py --server.port=8501 --server.address=0.0.0.0 &
streamlit run app/predicao_custos.py --server.port=8502 --server.address=0.0.0.0 &

# Mantém o container ativo
wait