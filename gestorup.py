import streamlit as st
import sqlite3
from datetime import date

# ======== CONEXÃO COM BANCO =========
conn = sqlite3.connect("produtos.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS produtos (
    codigo TEXT PRIMARY KEY,
    descricao TEXT NOT NULL
)
""")
conn.commit()

# ========= VARIÁVEIS DE SESSÃO =========
if 'descricao' not in st.session_state:
    st.session_state.descricao = ""

# ========= INTERFACE =========
st.title("🧊 Registro de Validade")
st.caption("Selecione a base de produtos (.xlsx)")

# === INÍCIO DO FORMULÁRIO ===
with st.form("formulario_registro"):

    codigo_produto = st.text_input("Código do Produto")

    buscar = st.form_submit_button("🔍 Buscar na base de produtos")

    # === BUSCAR DESCRIÇÃO PELO CÓDIGO NO BANCO ===
    if buscar:
        cursor.execute("SELECT descricao FROM produtos WHERE codigo = ?", (codigo_produto,))
        resultado = cursor.fetchone()
        if resultado:
            st.session_state.descricao = resultado[0]
            st.success("Produto encontrado.")
        else:
            st.session_state.descricao = ""
            st.warning("Produto não encontrado. Preencha manualmente.")

    descricao = st.text_input("Descrição", value=st.session_state.descricao)

    validade = st.date_input("Data de Validade", value=date.today())
    preco_atual = st.number_input("Preço Atual", min_value=0.0, format="%.2f")
    preco_queima = st.number_input("Preço de Queima de Estoque", min_value=0.0, format="%.2f")
    custo_atual = st.number_input("Custo Atual", min_value=0.0, format="%.2f")
    custo_anterior = st.number_input("Custo Anterior", min_value=0.0, format="%.2f")

    unidade = st.radio("Unidade", ["UN", "KG"], horizontal=True)

    salvar = st.form_submit_button("💾 Salvar Produto")

    if salvar:
        if not codigo_produto or not descricao:
            st.error("Código e Descrição são obrigatórios.")
        else:
            st.success("Produto registrado com sucesso! (Salvar lógica no banco se necessário)")

# ========== RODAPÉ ==========
st.caption("Desenvolvido por Gabriel dos Anjos")
