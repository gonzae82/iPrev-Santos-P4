import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from io import StringIO
import re 
from urllib.parse import urlparse # Necessário se usássemos o módulo urllib

# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
DB_USER = "root"
DB_PASS = "iprev123"
DB_HOST = "mysql-iprevsantos"
DB_PORT = "3306"
DB_NAME = "iprev_dados"
DB_TABLE = "despesas" 

# --- FUNÇÃO DE CONEXÃO (MANTIDA) ---
def get_db_engine():
    """Cria e retorna uma engine de conexão SQLAlchemy."""
    try:
        connection_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_url, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# --- FUNÇÃO ROBUSTA PARA LIMPAR NOMES DE COLUNA (MANTIDA) ---
def clean_column_name(col):
    """Converte nomes de coluna para o padrão MySQL (minúsculas, sem acento, com underscore)."""
    
    col = col.lower()
    col = col.replace('ê', 'e').replace('ã', 'a').replace('ç', 'c').replace('á', 'a').replace('ó', 'o')
    col = re.sub(r'[^a-z0-9_]+', '_', col)
    col = col.strip('_')
    col = col.replace('__', '_')
    
    return col

# --- FUNÇÃO DE LIMPEZA E TRANSFORMAÇÃO DE DADOS (MANTIDA) ---
def process_data(df):
    """Ajusta os tipos de dados da planilha para importação, focando na coluna CUSTO e MES."""
    
    money_columns = ['custo'] 
    
    if 'mes' in df.columns:
        df['mes'] = pd.to_datetime(df['mes'], errors='coerce')
    
    for col in money_columns:
        if col in df.columns:
            cleaned_col = (
                df[col].astype(str)
                .str.replace(r'R\$\s*', '', regex=True)
                .str.replace(',', '', regex=False)
            )
            df[col] = pd.to_numeric(cleaned_col, errors='coerce').fillna(0.0)
            
    return df

# --- NOVO: FUNÇÃO PARA CONSTRUIR O LINK ---
def build_prediction_link():
    
    host = "localhost"
    PRED_PORT = "8502"
    PRED_PATH = ""
    
    # Constrói o link completo com o host e porta fixados
    return f"http://{host}:{PRED_PORT}/{PRED_PATH}"


# --- INTERFACE DO STREAMLIT ---
st.set_page_config(page_title="Importador IPREVSANTOS", layout="wide")
st.title("🚀 Importador de Dados (TABELA FATO TAXAS & FUNDO)")

# --- BOTÃO DE NAVEGAÇÃO ---
link_predicao = build_prediction_link()
st.link_button("📊 Ir para a Predição de Custos", link_predicao)
st.markdown("---")

uploaded_file = st.file_uploader(
    "Selecione a planilha",
    type=['csv', 'xlsx']
)

if uploaded_file:
    st.subheader("🕵️‍♂️ Análise do Arquivo")
    
    tab1, tab2, tab3, tab4 = st.tabs(["1. Leitura do Arquivo", "2. Limpeza Nomes", "3. Conversão de Tipos", "4. Verificação Final"])
    
    try:
        # ETAPA 1: Leitura do Arquivo
        with tab1:
            st.write("Lendo o arquivo e exibindo as primeiras 5 linhas e as colunas originais.")
            if uploaded_file.name.endswith('.csv'):
                try:
                    df_raw = pd.read_csv(uploaded_file, sep='\t', encoding='utf-8')
                except:
                    df_raw = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
            else:
                df_raw = pd.read_excel(uploaded_file)
            
            st.dataframe(df_raw.head())
            st.write("**Colunas Lidas (RAW):**")
            st.code(df_raw.columns.tolist())

        # ETAPA 2: Limpeza Mínima dos Nomes das Colunas
        with tab2:
            st.write("Ajustando nomes de colunas para o padrão do banco de dados.")
            df_cleaned_cols = df_raw.copy()
            df_cleaned_cols.columns = [clean_column_name(col) for col in df_raw.columns]
            st.write("**Colunas Após Limpeza (BD Standard):**")
            st.code(df_cleaned_cols.columns.tolist())

        # ETAPA 3: Conversão dos Tipos de Dados
        with tab3:
            st.write("Convertendo colunas financeiras (custo) para formato numérico.")
            df_processed = process_data(df_cleaned_cols.copy()) 
            st.write("**Amostra dos Dados Após Conversão:**")
            st.dataframe(df_processed[['custo', 'ano', 'mes']].head())
            
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
                
                if 'id' in intersecting_columns:
                    intersecting_columns.remove('id')
                    
                missing_in_file = [col for col in db_columns if col not in file_columns and col != 'id']
                if missing_in_file:
                    st.warning(f"⚠️ **Atenção: Colunas do BD que faltam no arquivo (serão preenchidas com NULL/Default):** {missing_in_file}")


        st.markdown("---")
        # Botão de importação
        if st.button(f"▶️ Iniciar Importação para `{DB_TABLE}`"):
            engine = get_db_engine()
            if engine:
                db_columns = pd.read_sql(f"SELECT * FROM {DB_TABLE} LIMIT 0", engine).columns.tolist()
                
                cols_to_import = [col for col in db_columns if col in df_processed.columns]
                if 'id' in cols_to_import:
                    cols_to_import.remove('id')
                
                df_to_import = df_processed[cols_to_import]

                if df_to_import.empty or len(df_to_import.columns) == 0:
                     st.error("ERRO: Importação interrompida. Nenhuma coluna de dados correspondente foi encontrada. Verifique a aba '4. Verificação Final'.")
                else:
                    with st.spinner("Importando dados..."):
                        df_to_import.to_sql(DB_TABLE, con=engine, if_exists='append', index=False)
                        st.success("🎉 Importação concluída com sucesso!")

    except Exception as e:
        st.error(f"Erro Crítico durante o processamento: {e}")

# --- VISUALIZAÇÃO DOS DADOS NO BANCO
st.markdown("---")
with st.expander(f"Visualização dos Dados Atuais no Banco de Dados: Tabela :: {DB_TABLE}", expanded=False):
    engine = get_db_engine()
    if engine:
        try:
            df_from_db = pd.read_sql(f"SELECT * FROM {DB_TABLE} ORDER BY id DESC LIMIT 10", engine)
            st.dataframe(df_from_db)
        except Exception as e:
            st.warning(f"Não foi possível carregar os dados do banco. Erro: {e}")