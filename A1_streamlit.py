import os
import re
from datetime import date, datetime

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Configurações gerais
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Cadastro de Pacientes", layout="centered")


PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_CSV = os.path.join(PASTA, "pacientes.csv")


COLUNAS = [
    "timestamp",
    "nome",
    "data_nascimento",
    "idade",
    "email",
    "telefone",
    "possui_convenio",
    "convenio",
    "atendimento_particular",
    "prioridade",
    "motivo",
]


ROTULOS_TABELA = {
    "timestamp": "Data Do Cadastro",
    "nome": "Nome Completo",
    "data_nascimento": "Data De Nascimento",
    "idade": "Idade",
    "email": "E-mail",
    "telefone": "Telefone",
    "possui_convenio": "Possui Convênio",
    "convenio": "Convênio",
    "atendimento_particular": "Atendimento Particular",
    "prioridade": "Prioridade",
    "motivo": "Motivo Da Consulta",
}

CONVENIOS = ["Unimed", "Vera Cruz", "Bradesco Saúde", "SulAmérica", "Outro"]

REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# ---------------------------------------------------------------------------
# Cores
# ---------------------------------------------------------------------------
# As cores principais do tema (campos brancos, destaque azul em vez de
# vermelho/laranja) ficam no arquivo .streamlit/config.toml.
# O CSS abaixo cuida do resto e serve de reforço caso o tema não seja lido.
AZUL_MARINHO = "#1F3A5F"   # fundo da página
CINZA_CLARO = "#E9EDF2"    # fundo da ficha
CINZA_BORDA = "#C9D2DC"    # bordas dos campos
TEXTO = "#1F2937"          # texto escuro
AZUL_FOCO = "#4A6FA5"      # destaque: campo selecionado, botão Cadastrar, opção marcada
AZUL_FOCO_HOVER = "#3B5B8A"
CINZA_BOTAO = "#D5DCE5"    # botão Limpar Ficha e Baixar CSV

st.markdown(
    f"""
    <style>
    /* ---------- Página ---------- */
    .stApp, [data-testid="stHeader"] {{
        background-color: {AZUL_MARINHO};
    }}
    /* Textos fora da ficha ficam brancos (estão sobre o azul) */
    .stApp h1, .stApp h2, .stApp h3,
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stWidgetLabel"] p,
    .stApp [data-testid="stRadio"] label p {{
        color: #FFFFFF;
    }}

    /* ---------- Possui Convênio? (botões de opção) ---------- */
    /* Círculo não marcado: anel cinza claro com miolo branco */
    [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {{
        background-color: {CINZA_BORDA} !important;
    }}
    [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child > div {{
        background-color: #FFFFFF !important;
    }}
    /* Círculo marcado: azul com miolo branco */
    [data-testid="stRadio"] [data-baseweb="radio"]:has(input:checked) > div:first-child {{
        background-color: {AZUL_FOCO} !important;
    }}

    /* ---------- Ficha (st.form) ---------- */
    [data-testid="stForm"] {{
        background-color: {CINZA_CLARO};
        border: 1px solid {CINZA_BORDA};
        border-radius: 12px;
    }}
    /* Textos dentro da ficha ficam escuros */
    [data-testid="stForm"] [data-testid="stWidgetLabel"] p,
    [data-testid="stForm"] label p,
    [data-testid="stForm"] [data-testid="stMarkdownContainer"] p {{
        color: {TEXTO} !important;
    }}

    /* Campos: fundo branco e texto escuro (inclui Data de Nascimento).
       O Streamlit pinta a "caixa" em volta do campo, não só o <input>,
       por isso as caixas (data-baseweb) também entram aqui. */
    [data-testid="stForm"] [data-baseweb="input"],
    [data-testid="stForm"] [data-baseweb="input"] > div,
    [data-testid="stForm"] [data-baseweb="base-input"],
    [data-testid="stForm"] [data-baseweb="textarea"],
    [data-testid="stForm"] [data-baseweb="select"] > div,
    [data-testid="stForm"] input,
    [data-testid="stForm"] textarea {{
        background-color: #FFFFFF !important;
        color: {TEXTO} !important;
        caret-color: {TEXTO};
    }}
    [data-testid="stForm"] [data-baseweb="input"],
    [data-testid="stForm"] [data-baseweb="textarea"],
    [data-testid="stForm"] [data-baseweb="select"] > div {{
        border-color: {CINZA_BORDA} !important;
    }}
    [data-testid="stForm"] [data-baseweb="select"] * {{
        color: {TEXTO} !important;
    }}
    /* Campo selecionado: só a borda fica azul */
    [data-testid="stForm"] [data-baseweb="input"]:focus-within,
    [data-testid="stForm"] [data-baseweb="textarea"]:focus-within,
    [data-testid="stForm"] [data-baseweb="select"] > div:focus-within {{
        border-color: {AZUL_FOCO} !important;
    }}
    /* Valor do slider de prioridade em azul */
    [data-testid="stForm"] [role="slider"] {{
        background-color: {AZUL_FOCO} !important;
        border-color: {AZUL_FOCO} !important;
    }}
    [data-testid="stThumbValue"] {{
        color: {AZUL_FOCO} !important;
    }}

    /* ---------- Botões ---------- */
    /* Cadastrar: azul com texto branco */
    button[kind="primaryFormSubmit"] {{
        background-color: {AZUL_FOCO} !important;
        border-color: {AZUL_FOCO} !important;
        color: #FFFFFF !important;
    }}
    button[kind="primaryFormSubmit"]:hover {{
        background-color: {AZUL_FOCO_HOVER} !important;
        border-color: {AZUL_FOCO_HOVER} !important;
    }}
    /* Limpar Ficha e Baixar CSV: cinza-azulado com texto escuro */
    button[kind="secondaryFormSubmit"],
    button[kind="secondary"] {{
        background-color: {CINZA_BOTAO} !important;
        border-color: {CINZA_BORDA} !important;
        color: {TEXTO} !important;
    }}
    button[kind="secondaryFormSubmit"]:hover,
    button[kind="secondary"]:hover {{
        background-color: {CINZA_BORDA} !important;
        color: {TEXTO} !important;
    }}
    /* O texto do botão herda a cor definida acima */
    button[kind] p {{
        color: inherit !important;
    }}

    /* ---------- Mensagens de sucesso/erro ---------- */
    [data-testid="stAlert"] p {{
        color: {TEXTO} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Funções auxiliares (iguais às da versão Gradio)
# ---------------------------------------------------------------------------
def calcular_idade(nascimento, hoje=None):
    """Idade em anos completos: desconta 1 se o aniversário deste ano ainda não chegou."""
    hoje = hoje or date.today()
    ainda_nao_fez_aniversario = (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    return hoje.year - nascimento.year - ainda_nao_fez_aniversario


def formatar_telefone(telefone):
    """Aceita só números (com DDD) e devolve no formato (11) 91234-5678.
    Devolve None se a quantidade de dígitos não for 10 (fixo) ou 11 (celular)."""
    digitos = re.sub(r"\D", "", telefone or "")
    if len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return None


def ler_arquivo():
    """Lê o CSV do disco (ou devolve uma tabela vazia se ele ainda não existe)."""
    if os.path.exists(ARQUIVO_CSV):
        dados = pd.read_csv(ARQUIVO_CSV, dtype=str, keep_default_na=False)
        return dados.reindex(columns=COLUNAS, fill_value="")
    return pd.DataFrame(columns=COLUNAS)


def gravar_no_csv(linha):
    """Mesma lógica da versão Gradio: lê o arquivo, junta a linha nova e regrava."""
    dados = pd.concat([ler_arquivo(), pd.DataFrame([linha], columns=COLUNAS)], ignore_index=True)
    dados.to_csv(ARQUIVO_CSV, index=False)


def validar_e_montar_linha(nome, nascimento, email, telefone, possui_convenio,
                           convenio, prioridade, motivo):
    """Devolve (linha, None) se estiver tudo certo, ou (None, mensagem_de_erro)."""
    if not nome or not nome.strip():
        return None, "Informe o nome do paciente."

    if nascimento is None:
        return None, "Informe a data de nascimento."
    if nascimento > date.today():
        return None, "A data de nascimento não pode estar no futuro."
    idade = calcular_idade(nascimento)
    if idade > 130:
        return None, "Confira a data de nascimento (idade acima de 130 anos)."

    email = (email or "").strip()
    if not REGEX_EMAIL.match(email):
        return None, "Informe um e-mail válido (ex.: nome@dominio.com)."

    telefone_formatado = formatar_telefone(telefone)
    if telefone_formatado is None:
        return None, "Informe o telefone com DDD (10 ou 11 dígitos)."

    tem_convenio = possui_convenio == "Sim"
    if tem_convenio and not convenio:
        return None, "Selecione o convênio."

    linha = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nome": nome.strip(),
        "data_nascimento": nascimento.strftime("%d/%m/%Y"),
        "idade": idade,
        "email": email.lower(),
        "telefone": telefone_formatado,
        "possui_convenio": possui_convenio,
        "convenio": convenio if tem_convenio else "",
        # Sem convênio, a caixa "Atendimento Particular" está sempre marcada
        "atendimento_particular": "Não" if tem_convenio else "Sim",
        "prioridade": int(prioridade),
        "motivo": motivo or "",
    }
    return linha, None


# ---------------------------------------------------------------------------
# Estado da sessão (st.session_state)
# ---------------------------------------------------------------------------

ss = st.session_state

if "pacientes" not in ss:
    ss.pacientes = pd.DataFrame(columns=COLUNAS)  # cadastros desta sessão
if "mensagem" not in ss:
    ss.mensagem = None                            # ("sucesso" | "erro", texto)


VALORES_INICIAIS = {
    "possui_convenio": "Não",
    "nome": "",
    "data_nascimento": None,
    "email": "",
    "telefone": "",
    "prioridade": 1,
    "motivo": "",
}
for chave, valor in VALORES_INICIAIS.items():
    if chave not in ss:
        ss[chave] = valor


def limpar_campos():
    """Volta todos os campos aos valores iniciais."""
    for chave, valor in VALORES_INICIAIS.items():
        ss[chave] = valor
    ss.pop("convenio", None)


# ---------------------------------------------------------------------------
# Ações dos botões
# ---------------------------------------------------------------------------

def ao_cadastrar():
    linha, erro = validar_e_montar_linha(
        ss.nome, ss.data_nascimento, ss.email, ss.telefone,
        ss.possui_convenio, ss.get("convenio"), ss.prioridade, ss.motivo,
    )
    if erro:
        # Os campos NÃO são limpos, para o usuário corrigir só o que faltou
        ss.mensagem = ("erro", f"Erro: {erro}")
        return

    # 1) Acumula na sessão
    ss.pacientes = pd.concat(
        [ss.pacientes, pd.DataFrame([linha], columns=COLUNAS)], ignore_index=True
    )
    # 2) Grava no CSV do disco (mesma lógica da versão Gradio)
    gravar_no_csv(linha)

    ss.mensagem = ("sucesso", "Paciente cadastrado com sucesso!")
    limpar_campos()


def ao_limpar():
    limpar_campos()
    ss.mensagem = None


# ---------------------------------------------------------------------------
# Interface
# ---------------------------------------------------------------------------
st.title("Cadastro de Pacientes")


st.radio("Possui Convênio?", ["Sim", "Não"], key="possui_convenio", horizontal=True)

with st.form("cadastro"):
    st.text_input("Nome Completo", key="nome")
    st.date_input(
        "Data de Nascimento",
        key="data_nascimento",
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        format="DD/MM/YYYY",
    )
    st.text_input("E-mail", key="email", placeholder="nome@dominio.com")
    st.text_input("Telefone", key="telefone", placeholder="(11) 91234-5678")

    if ss.possui_convenio == "Sim":
        st.selectbox("Convênio", CONVENIOS, key="convenio", index=None,
                     placeholder="Selecione o convênio")
    else:
        st.checkbox("Atendimento Particular", value=True, disabled=True)

    st.slider("Prioridade do Atendimento", 1, 5, step=1, key="prioridade")
    st.text_area("Motivo da Consulta / Observações", key="motivo")

    col1, col2 = st.columns(2)
    with col1:
        st.form_submit_button("Cadastrar", on_click=ao_cadastrar, type="primary")
    with col2:
        st.form_submit_button("Limpar Ficha", on_click=ao_limpar)

# Mensagem de status
if ss.mensagem:
    tipo, texto = ss.mensagem
    if tipo == "sucesso":
        st.success(texto)
    else:
        st.error(texto)

# Tabela com os últimos cadastros da sessão
st.subheader("Últimos Pacientes Cadastrados")
if ss.pacientes.empty:
    st.caption("Nenhum paciente cadastrado nesta sessão.")
else:
    st.dataframe(ss.pacientes.tail(5).rename(columns=ROTULOS_TABELA), hide_index=True)

# Download do CSV com os cadastros da sessão
# "utf-8-sig" faz o Excel reconhecer os acentos corretamente.
csv_sessao = ss.pacientes.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Baixar CSV",
    data=csv_sessao,
    file_name=f"pacientes_{datetime.now():%Y-%m-%d}.csv",
    mime="text/csv",
    disabled=ss.pacientes.empty,
)
st.caption(
    f"{len(ss.pacientes)} paciente(s) cadastrado(s) nesta sessão. "
    "No Streamlit Community Cloud o arquivo salvo no servidor é apagado quando "
    "o app reinicia: baixe o CSV para não perder os dados."
)
