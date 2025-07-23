import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Gestor de Validade", layout="wide")
st.image("logo.png", width=100)

# ----- SESSÃO -----
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""

# ----- LOGIN -----
if not st.session_state["logado"]:
    st.subheader("Login do Sistema")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == "admin" and senha == "79318520":
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# ----- BOTÃO DE SAIR -----
with st.sidebar:
    st.markdown(f"👤 Usuário: **{st.session_state['usuario']}**")
    if st.button("🚪 Sair"):
        st.session_state["logado"] = False
        st.session_state["usuario"] = ""
        st.experimental_rerun()

# ----- CONEXÃO COM BANCO -----
db_path = "produtos.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ----- CRIAÇÃO DA TABELA (caso não exista) -----
cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    codigo TEXT,
    descricao TEXT,
    validade TEXT,
    qtd TEXT,
    preco_atual TEXT,
    preco_queima TEXT,
    custo_atual TEXT,
    custo_anterior TEXT
)
""")
conn.commit()

st.title("📦 Gestor de Validade de Produtos")

# ----- VERIFICA SE JÁ EXISTE DADOS NO BANCO -----
df = pd.read_sql_query("SELECT * FROM produtos", conn)
if df.empty:
    st.warning("Nenhum dado encontrado. Faça o upload da base com colunas 'codigo' e 'descricao'.")
    uploaded_file = st.file_uploader("📁 Upload da base inicial", type=["xlsx"])
    if uploaded_file:
        df_upload = pd.read_excel(uploaded_file)
        if "codigo" in df_upload.columns and "descricao" in df_upload.columns:
            df_upload.to_sql("produtos", conn, index=False, if_exists="append")
            st.success("Base carregada com sucesso! Recarregue a página.")
            st.stop()
        else:
            st.error("A base deve conter as colunas 'codigo' e 'descricao'.")
            st.stop()

# ----- FORMULÁRIO DE REGISTRO DE PRODUTO -----
st.subheader("📋 Cadastro de Produto")
with st.form("formulario"):
    cod = st.text_input("Código do produto")
    desc = ""

    # Preenche a descrição automaticamente
    if cod:
        cursor.execute("SELECT descricao FROM produtos WHERE codigo = ? LIMIT 1", (cod,))
        resultado = cursor.fetchone()
        if resultado:
            desc = resultado[0]

    st.text_input("Descrição", value=desc, disabled=True)
    validade = st.date_input("Validade do produto")
    qtd = st.text_input("Quantidade (un ou kg)")
    preco_atual = st.text_input("Preço atual")
    preco_queima = st.text_input("Preço de queima de estoque")
    custo_atual = st.text_input("Custo atual")
    custo_anterior = st.text_input("Custo anterior")

    enviar = st.form_submit_button("Salvar")
    if enviar:
        cursor.execute("""
            INSERT INTO produtos (codigo, descricao, validade, qtd, preco_atual, preco_queima, custo_atual, custo_anterior)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (cod, desc, validade.strftime("%Y-%m-%d"), qtd, preco_atual, preco_queima, custo_atual, custo_anterior))
        conn.commit()
        st.success("Produto salvo com sucesso!")

# ----- VISUALIZAR PRODUTOS CADASTRADOS -----
st.subheader("🔍 Produtos Cadastrados")
df = pd.read_sql_query("SELECT * FROM produtos", conn)
st.dataframe(df, use_container_width=True)
