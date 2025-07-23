import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# ========== CONEXÃO COM O BANCO DE DADOS ==========
conn_produtos = sqlite3.connect('produtos.db', check_same_thread=False)
cursor_produtos = conn_produtos.cursor()

conn_usuarios = sqlite3.connect('usuarios.db', check_same_thread=False)
cursor_usuarios = conn_usuarios.cursor()
cursor_usuarios.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    usuario TEXT PRIMARY KEY,
    senha TEXT NOT NULL
)
""")
conn_usuarios.commit()

# ========== VARIÁVEIS DE SESSÃO ==========
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# ========== LOGIN ==========
def login():
    st.title("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        cursor_usuarios.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
        if cursor_usuarios.fetchone():
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# ========== CADASTRO DE USUÁRIO (apenas admin) ==========
def cadastrar_usuario():
    st.subheader("Cadastro de Novo Usuário (Admin apenas)")
    nova_senha_admin = st.text_input("Senha do Administrador", type="password")
    if nova_senha_admin == "79318520":
        novo_usuario = st.text_input("Novo Usuário")
        nova_senha = st.text_input("Nova Senha", type="password")
        if st.button("Cadastrar"):
            cursor_usuarios.execute("INSERT OR IGNORE INTO usuarios (usuario, senha) VALUES (?, ?)", (novo_usuario, nova_senha))
            conn_usuarios.commit()
            st.success("Usuário cadastrado com sucesso!")
    else:
        st.warning("Senha de administrador incorreta.")

# ========== PÁGINA PRINCIPAL ==========
def app():
    st.title("📦 Registro de Validade")

    # Upload opcional (caso deseje trocar a base manualmente futuramente)
    st.caption("Selecione a base de produtos (.xlsx)")
    arquivo = st.file_uploader("Drag and drop file here", type=["xlsx"])

    # Conexão com banco de produtos
    cursor_produtos.execute("CREATE TABLE IF NOT EXISTS produtos (codigo TEXT PRIMARY KEY, descricao TEXT)")
    conn_produtos.commit()

    if arquivo:
        df_base = pd.read_excel(arquivo, dtype=str)
        df_base.columns = df_base.columns.str.lower()
        if 'codigo' in df_base.columns and 'descricao' in df_base.columns:
            for index, row in df_base.iterrows():
                cursor_produtos.execute("INSERT OR IGNORE INTO produtos (codigo, descricao) VALUES (?, ?)", (str(row['codigo']), row['descricao']))
            conn_produtos.commit()
            st.success("Base carregada com sucesso.")

    with st.form("form_validade"):
        codigo = st.text_input("Código do Produto")
        buscar = st.form_submit_button("🔍 Buscar na base de produtos")

        descricao = ""
        if buscar:
            cursor_produtos.execute("SELECT descricao FROM produtos WHERE codigo=?", (codigo,))
            resultado = cursor_produtos.fetchone()
            if resultado:
                descricao = resultado[0]
                st.success("Produto encontrado.")
            else:
                st.warning("Produto não encontrado. Preencha a descrição manualmente.")

        descricao = st.text_input("Descrição", value=descricao)
        validade = st.date_input("Data de Validade", value=date.today())
        preco_atual = st.text_input("Preço Atual")
        preco_queima = st.text_input("Preço Queima de Estoque")
        custo_atual = st.text_input("Custo Atual")
        custo_anterior = st.text_input("Custo Anterior")
        quantidade = st.text_input("Quantidade (UN ou KG)")

        salvar = st.form_submit_button("Salvar Registro")
        if salvar:
            st.success("Produto registrado com sucesso!")

    if st.session_state.usuario == "admin":
        with st.expander("👤 Gerenciar Usuários"):
            cadastrar_usuario()

    if st.button("Sair"):
        st.session_state.logado = False
        st.session_state.usuario = ""
        st.experimental_rerun()

# ========== EXECUÇÃO ==========
if not st.session_state.logado:
    login()
else:
    app()
