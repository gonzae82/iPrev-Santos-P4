import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from prophet import Prophet
from prophet.plot import plot_plotly
from pandas.tseries.offsets import MonthBegin
import plotly.graph_objects as go
from datetime import datetime, date

# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
DB_USER = "root"
DB_PASS = "iprev123"
DB_HOST = "mysql-iprevsantos"
DB_PORT = "3306"
DB_NAME = "iprev_dados"
DB_TABLE = "despesas"

# --- FUNÇÃO DE CONEXÃO ---
@st.cache_resource
def get_db_engine():
    """Cria e retorna uma engine de conexão SQLAlchemy."""
    try:
        connection_url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_url, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# --- 1. CARREGAMENTO E PREPARAÇÃO DOS DADOS (MODIFICADA) ---
@st.cache_data(ttl=600) 
def load_and_prepare_data():
    """
    Carrega TODOS os dados de custo mensais do banco.
    Retorna o DataFrame e as datas min/max para o seletor.
    """
    engine = get_db_engine()
    if engine is None:
        return None, None, None

    st.info("Carregando e agregando todos os dados mensais do MySQL...")
    
    # Consulta SQL para agregar os custos mensalmente
    sql_query = f"""
    SELECT
        DATE_FORMAT(mes, '%Y-%m-01') AS ds,
        SUM(custo) AS y
    FROM
        {DB_TABLE}
    GROUP BY
        ds 
    ORDER BY
        ds;
    """
    
    try:
        df = pd.read_sql(sql_query, engine)
        
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.dropna(subset=['y'])
        
        # Calcula as datas min/max para o seletor de Streamlit
        min_date = df['ds'].min().date()
        max_date = df['ds'].max().date()
        
        return df, min_date, max_date
        
    except Exception as e:
        st.error(f"Erro ao carregar ou processar dados do banco: {e}")
        return None, None, None

# --- 2. MODELAGEM E PREDIÇÃO ---
def run_forecasting(df_history, periods=12):
    """
    Treina o modelo Prophet e gera a previsão.
    """
    # 1. Cria e configura o modelo Prophet
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative' 
    )
    
    # 2. Treina o modelo
    model.fit(df_history)
    
    # 3. Cria um DataFrame para a previsão
    future = model.make_future_dataframe(periods=periods, freq='MS')
    
    # 4. Faz a previsão
    forecast = model.predict(future)
    
    return model, forecast

# --- 3. INTERFACE DO STREAMLIT ---
st.set_page_config(page_title="Predição de Custos", layout="wide")
st.title("🔮 Predição de Custos Futuros")
st.markdown("---")

# Carregar dados (apenas uma vez, no início)
df_all, min_db_date, max_db_date = load_and_prepare_data()

if df_all is None or df_all.empty:
    st.error("Não foi possível carregar dados para a predição. Verifique a conexão com o banco e a tabela.")
    st.stop()
    
# --- CONFIGURAÇÕES NA BARRA LATERAL ---
st.sidebar.header("Configurações de Predição")

# 1. Seleção do Período de Treinamento
st.sidebar.subheader("Período de Análise Histórica")

# Define o valor padrão dos seletores como o período máximo disponível no banco
default_start = min_db_date
default_end = max_db_date

start_date = st.sidebar.date_input(
    "Data de Início (Treinamento)", 
    value=default_start,
    min_value=min_db_date,
    max_value=max_db_date
)

end_date = st.sidebar.date_input(
    "Data de Fim (Treinamento)", 
    value=default_end,
    min_value=min_db_date,
    max_value=max_db_date
)

if start_date >= end_date:
    st.sidebar.error("A Data de Início deve ser anterior à Data de Fim.")
    st.stop()

# 2. Meses para Predizer
n_periods = st.sidebar.slider("Meses para Predizer", 6, 24, 12)

# --- BOTÃO PARA INICIAR A PREDIÇÃO ---
st.markdown("### 1. Dados Históricos Selecionados")

# Filtra o DataFrame original com base nas datas selecionadas
df_historical = df_all[(df_all['ds'].dt.date >= start_date) & (df_all['ds'].dt.date <= end_date)].copy()

st.info(f"Serão usados **{len(df_historical)}** meses de dados, de **{start_date.strftime('%Y-%m')}** a **{end_date.strftime('%Y-%m')}**.")
st.dataframe(df_historical.head(5))

# Botão para iniciar o processo
if st.button("▶️ Gerar Predição de Custos"):
    
    if len(df_historical) < 24:
        st.warning(f"O Prophet geralmente requer pelo menos 24 pontos (meses) para detectar bem a sazonalidade. Você está usando apenas {len(df_historical)} meses.")
    
    st.markdown("---")
    st.markdown(f"### 2. Resultados da Predição ({n_periods} Meses)")

    # Treinar e prever
    with st.spinner(f"Treinando modelo Prophet e prevendo os próximos {n_periods} meses..."):
        prophet_model, df_forecast = run_forecasting(df_historical, periods=n_periods)
    
    st.success("Previsão concluída!")
    
    # --- VISUALIZAÇÃO ---
    st.subheader("Gráfico de Previsão de Custos")
    
    # Cria o gráfico interativo
    fig = plot_plotly(
        prophet_model, 
        df_forecast, 
        xlabel="Data", 
        ylabel="Custo Total (R$)", 
        changepoints=False
    )
    
    # Personaliza o gráfico e otimiza a legenda
    fig.update_layout(
        title_text=f"Custo Histórico e Previsão de {n_periods} Meses",
        yaxis_tickprefix = 'R$ ',
        hovermode="x unified"
    )
    fig.data[0].name = 'Custo Histórico'
    fig.data[1].name = 'Intervalo de Incerteza (80%)'
    fig.data[2].name = 'Custo Predito'
    fig.update_traces(showlegend=True)

    # Adiciona linha vertical para separar histórico e previsão
    last_historical_date = df_historical['ds'].max()
    separation_date_timestamp = last_historical_date + MonthBegin(1)
    separation_date_str = separation_date_timestamp.strftime('%Y-%m-%d')
    
    fig.add_vline(
        x=separation_date_str, 
        line_width=2, 
        line_dash="dash", 
        line_color="red"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # --- TABELA DE PREVISÃO ---
    st.subheader("Tabela de Predição para os Próximos Meses")
    
    future_forecast = df_forecast[df_forecast['ds'] > last_historical_date].copy()
    
    # Função de formatação para R$
    def format_brl(value):
        return f"R$ {value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")

    future_forecast['Mês/Ano'] = future_forecast['ds'].dt.strftime('%Y-%m')
    future_forecast['Custo (Predito)'] = future_forecast['yhat'].apply(format_brl)
    future_forecast['Limite Inferior (80%)'] = future_forecast['yhat_lower'].apply(format_brl)
    future_forecast['Limite Superior (80%)'] = future_forecast['yhat_upper'].apply(format_brl)
    
    st.dataframe(
        future_forecast[['Mês/Ano', 'Custo (Predito)', 'Limite Inferior (80%)', 'Limite Superior (80%)']],
        hide_index=True
    )