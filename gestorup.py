import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime

# ========== BANCO DE DADOS ==========

# Usuários
conn_usuarios = sqlite3.connect("usuarios.db", check_same_thread=False)
cursor_usuarios = conn_usuarios.cursor()
cursor_usuarios.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    usuario TEXT PRIMARY KEY,
    senha TEXT NOT NULL
)
""")
conn_usuarios.commit()

# Validade
conn_validade = sqlite3.connect("validade.db", check_same_thread=False)
cursor_validade = conn_validade.cursor()
cursor_validade.execute("""
CREATE TABLE IF NOT EXISTS validade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    descricao TEXT,
    validade TEXT,
    preco_atual REAL,
    preco_queima REAL,
    custo_atual REAL,
    custo_anterior REAL,
    quantidade REAL,
    unidade TEXT
)
""")
conn_validade.commit()

# ========== VARIÁVEIS DE SESSÃO ==========

if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# ========== FUNÇÕES AUXILIARES ==========

def verificar_login(usuario, senha):
    cursor_usuarios.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    return cursor_usuarios.fetchone()

def cadastrar_usuario(usuario, senha):
    try:
        cursor_usuarios.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
        conn_usuarios.commit()
        return True
    except:
        return False

def dias_para_vencer(data_validade):
    hoje = date.today()
    return (data_validade - hoje).days

def salvar_registro(novo):
    cursor_validade.execute("""
        INSERT INTO validade (codigo, descricao, validade, preco_atual, preco_queima, custo_atual, custo_anterior, quantidade, unidade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        novo["Código"], novo["Descrição"], novo["Validade"].strftime("%Y-%m-%d"), novo["Preço Atual"], novo["Preço Queima"],
        novo["Custo Atual"], novo["Custo Anterior"], novo["Quantidade"], novo["Unidade"]
    ))
    conn_validade.commit()

def carregar_registros():
    cursor_validade.execute("SELECT codigo, descricao, validade, preco_atual, preco_queima, custo_atual, custo_anterior, quantidade, unidade FROM validade")
    rows = cursor_validade.fetchall()
    if rows:
        df = pd.DataFrame(rows, columns=["Código", "Descrição", "Validade", "Preço Atual", "Preço Queima", "Custo Atual", "Custo Anterior", "Quantidade", "Unidade"])
        df["Validade"] = pd.to_datetime(df["Validade"]).dt.date
        df["Dias p/ Vencer"] = df["Validade"].apply(dias_para_vencer)
        return df
    else:
        return pd.DataFrame(columns=["Código", "Descrição", "Validade", "Preço Atual", "Preço Queima", "Custo Atual", "Custo Anterior", "Quantidade", "Unidade", "Dias p/ Vencer"])

# ========== CONFIGURAÇÕES INICIAIS ==========

st.set_page_config("Gestão de Validade", layout="wide")
st.title("🧾 Sistema de Controle de Validade de Produtos")

# ========== LOGIN E LOGOUT ==========

if not st.session_state.logado:
    st.subheader("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if verificar_login(usuario, senha) or (usuario == "admin" and senha == "79318520"):
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.success("Login realizado com sucesso.")
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()
else:
    # Botão sair
    if st.button("🔓 Sair"):
        st.session_state.logado = False
        st.session_state.usuario = ""
        st.experimental_rerun()

# ========== ABAS ==========

abas = st.tabs(["📥 Registro de Validade", "📄 Relação de Produtos"] + (["👤 Cadastro de Usuários"] if st.session_state.usuario == "admin" else []))

# ========== ABA: Registro de Validade ==========

with abas[0]:
    st.header("📥 Registro de Validade")

    uploaded_file = st.file_uploader("Selecione a base de produtos (.xlsx)", type="xlsx")

    mapa_desc = {}
    if uploaded_file:
        base = pd.read_excel(uploaded_file)
        base["codigo"] = base["codigo"].astype(str)
        mapa_desc = dict(zip(base["codigo"], base["descricao"]))
        st.success(f"Base carregada com {len(mapa_desc)} produtos.")

    with st.form("formulario_registro"):
        codigo_input = st.text_input("Código do Produto")
        descricao = mapa_desc.get(codigo_input.strip(), "")
        st.text_input("Descrição", value=descricao,)

        validade = st.date_input("Data de Validade", min_value=date.today())
        preco_atual = st.number_input("Preço Atual", min_value=0.0, step=0.01)
        preco_queima = st.number_input("Preço de Queima de Estoque", min_value=0.0, step=0.01)
        custo_atual = st.number_input("Custo Atual", min_value=0.0, step=0.01)
        custo_anterior = st.number_input("Custo Anterior", min_value=0.0, step=0.01)
        quantidade = st.number_input("Quantidade", min_value=0.0, step=1.0)
        unidade = st.selectbox("Unidade", ["Unidade", "Kg", "Litro", "Pacote", "Caixa"])

        enviado = st.form_submit_button("Salvar Registro")

    if enviado:
        if not codigo_input.strip():
            st.error("Por favor, informe o código do produto.")
        else:
            novo = {
                "Código": codigo_input.strip(),
                "Descrição": descricao_input,
                "Validade": validade,
                "Preço Atual": preco_atual,
                "Preço Queima": preco_queima,
                "Custo Atual": custo_atual,
                "Custo Anterior": custo_anterior,
                "Quantidade": quantidade,
                "Unidade": unidade
            }
            salvar_registro(novo)
            st.success("Produto registrado com sucesso.")

# ========== ABA: Relação de Produtos ==========

with abas[1]:
    st.header("📄 Relação de Produtos Registrados")

    df = carregar_registros()

    if df.empty:
        st.warning("Nenhum registro encontrado. Faça o upload e registre primeiro.")
    else:
        filtro = st.selectbox("Filtrar por:", ["Todos", "Hoje", "≤ 7 dias", "≤ 15 dias", "≤ 30 dias", "≤ 60 dias", "≤ 90 dias"])

        if filtro == "Hoje":
            df = df[df["Dias p/ Vencer"] == 0]
        elif filtro == "≤ 7 dias":
            df = df[df["Dias p/ Vencer"] <= 7]
        elif filtro == "≤ 15 dias":
            df = df[df["Dias p/ Vencer"] <= 15]
        elif filtro == "≤ 30 dias":
            df = df[df["Dias p/ Vencer"] <= 30]
        elif filtro == "≤ 60 dias":
            df = df[df["Dias p/ Vencer"] <= 60]
        elif filtro == "≤ 90 dias":
            df = df[df["Dias p/ Vencer"] <= 90]

        st.dataframe(df, use_container_width=True)

# ========== ABA: Cadastro de Usuários (apenas admin) ==========

if st.session_state.usuario == "admin":
    with abas[2]:
        st.header("👤 Cadastro de Usuários")
        with st.form("cadastro_form"):
            novo_usuario = st.text_input("Novo Usuário")
            nova_senha = st.text_input("Senha", type="password")
            confirmar_senha = st.text_input("Confirmar Senha", type="password")
            cadastrar = st.form_submit_button("Cadastrar")

        if cadastrar:
            if nova_senha != confirmar_senha:
                st.error("As senhas não coincidem.")
            elif not novo_usuario or not nova_senha:
                st.error("Preencha todos os campos.")
            else:
                if cadastrar_usuario(novo_usuario, nova_senha):
                    st.success(f"Usuário '{novo_usuario}' cadastrado com sucesso.")
                else:
                    st.error("Usuário já existe.")
