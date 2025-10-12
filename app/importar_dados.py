import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from io import StringIO

# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
DB_USER = "root"
DB_PASS = "iprev123"
DB_HOST = "mysql-iprevsantos"
DB_PORT = "3306"
DB_NAME = "iprev_dados"
DB_TABLE = "despesas"

# --- FUNÇÃO DE CONEXÃO ---
def get_db_engine():
    """Cria e retorna uma engine de conexão SQLAlchemy."""
    try:
        connection_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_url, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# --- FUNÇÃO DE LIMPEZA E TRANSFORMAÇÃO ---
def process_data(df):
    """Ajusta os tipos de dados da planilha para importação."""
    
    # Lista de colunas que devem ser numéricas (DECIMAL no DB)
    money_columns = [
        'VENCIMENTO', 'FUNCAO_RATIFICADA', 'GDA', 'S_13_SAL', 'S_13_SAL_2', 'ATS', 
        'REM_FERIAS', 'AUX_ALIM', 'FALTAS', 'SOMA', 'PATR_CAPEP', 'PATR_IPREV', 
        'PATR_INSS', 'PATR_CX_PREV', 'SOMA_2', 'CUSTO_TOTAL', 'CUSTO_HORA', 
        'CAPEP', 'IPREV', 'INSS', 'CX_PREVID'
    ]

    # Limpa e converte cada coluna monetária de forma segura
    for col in money_columns:
        if col in df.columns:
            cleaned_col = df[col].astype(str).str.replace(',', '.')
            df[col] = pd.to_numeric(cleaned_col, errors='coerce').fillna(0.0)
            
    return df

# --- INTERFACE DO STREAMLIT ---
st.set_page_config(page_title="Importador IPREVSANTOS", layout="wide")
st.title("🚀 Importador de Dados")

uploaded_file = st.file_uploader(
    "Selecione a planilha",
    type=['csv', 'xlsx']
)

if uploaded_file:
    st.markdown("---")
    st.subheader("🕵️‍♂️ Análise do Arquivo")
    
    tab1, tab2, tab3, tab4 = st.tabs(["1. Leitura do Arquivo", "2. Limpeza Mínima", "3. Conversão de Tipos", "4. Verificação Final"])
    
    try:
        # ETAPA 1: Leitura do Arquivo
        with tab1:
            st.write("Lendo o arquivo e exibindo as primeiras 5 linhas e as colunas originais.")
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file, sep=';')
            else:
                df_raw = pd.read_excel(uploaded_file)
            st.dataframe(df_raw.head())
            st.write("**Colunas Lidas:**")
            st.code(df_raw.columns.tolist())
            st.write(f"**Dimensões:** {df_raw.shape[0]} linhas, {df_raw.shape[1]} colunas")

        # ETAPA 2: Limpeza Mínima dos Nomes das Colunas
        with tab2:
            st.write("Removendo apenas espaços em branco do início e fim dos nomes das colunas.")
            df_cleaned_cols = df_raw.copy()
            # REMOVIDA A CONVERSÃO PARA MAIÚSCULAS
            df_cleaned_cols.columns = [col.strip() for col in df_raw.columns]
            st.write("**Colunas Após Limpeza Mínima:**")
            st.code(df_cleaned_cols.columns.tolist())

        # ETAPA 3: Conversão dos Tipos de Dados
        with tab3:
            st.write("Convertendo colunas financeiras para formato numérico.")
            df_processed = process_data(df_cleaned_cols.copy())
            st.write("**Amostra dos Dados Após Conversão:**")
            st.dataframe(df_processed.head())
            
            buffer = StringIO()
            df_processed.info(buf=buffer)
            s = buffer.getvalue()
            st.write("**Tipos de Dados Finais:**")
            st.text(s)

        # ETAPA 4: Verificação Final Antes de Importar
        with tab4:
            st.write("Comparando as colunas do arquivo com as colunas do banco de dados.")
            engine = get_db_engine()
            if engine:
                db_columns = pd.read_sql(f"SELECT * FROM {DB_TABLE} LIMIT 0", engine).columns.tolist()
                st.write("**Colunas Esperadas pelo Banco de Dados:**")
                st.code(db_columns)

                file_columns = df_processed.columns.tolist()
                st.write("**Colunas Encontradas no Arquivo (Processado):**")
                st.code(file_columns)
                
                intersecting_columns = [col for col in db_columns if col in file_columns]
                st.write("**Colunas na Interseção (que serão importadas):**")
                st.code(intersecting_columns)
                
                missing_in_db = [col for col in file_columns if col not in db_columns]
                if missing_in_db:
                    st.warning("**Atenção: Colunas no arquivo que não existem no banco:**")
                    st.code(missing_in_db)

        st.markdown("---")
        # Botão de importação
        if st.button(f"▶️ Iniciar Importação para `{DB_TABLE}`"):
            engine = get_db_engine()
            if engine:
                db_columns = pd.read_sql(f"SELECT * FROM {DB_TABLE} LIMIT 0", engine).columns.tolist()
                df_to_import = df_processed[[col for col in db_columns if col in df_processed.columns]]

                if df_to_import.empty or len(df_to_import.columns) == 0:
                     st.error("ERRO: Importação interrompida. Nenhuma coluna correspondente foi encontrada. Verifique a aba '4. Verificação Final' e garanta que os nomes das colunas (incluindo maiúsculas/minúsculas) são idênticos.")
                else:
                    with st.spinner("Importando dados..."):
                        df_to_import.to_sql(DB_TABLE, con=engine, if_exists='append', index=False)
                        st.success("🎉 Importação concluída com sucesso!")
                        #st.balloons()
    except Exception as e:
        st.error(f"Erro Crítico durante o processamento: {e}")

# --- VISUALIZAÇÃO DOS DADOS NO BANCO ---
st.markdown("---")
with st.expander(f"Visualização dos Dados Atuais no Banco de Dados: Tabela :: {DB_TABLE}", expanded=True):
    engine = get_db_engine()
    if engine:
        try:
            df_from_db = pd.read_sql(f"SELECT * FROM {DB_TABLE} ORDER BY id DESC", engine)
            st.dataframe(df_from_db)
        except Exception as e:
            st.warning("Não foi possível carregar os dados do banco.")