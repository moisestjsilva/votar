import streamlit as st
import pandas as pd
import os
from datetime import datetime
from calendar import month_name
import matplotlib.pyplot as plt
import seaborn as sns
import time

# Inicializar contadores de votos se não existirem na sessão
if 'votos' not in st.session_state:
    st.session_state.votos = {'Insatisfeito': 0, 'Neutro': 0, 'Satisfeito': 0}

# Função para atualizar votos
def votar(opcao):
    st.session_state.votos[opcao] += 1
    salvar_votos()

    # Mostrar mensagem de sucesso por 2 segundos
    mensagem = st.empty()
    mensagem.success(f'Voto registrado com sucesso: {opcao}')
    time.sleep(2)  # Manter a mensagem por 2 segundos
    mensagem.empty()  # Limpar a mensagem após o tempo definido

# Função para salvar votos em arquivo CSV
def salvar_votos():
    now = datetime.now()
    data = {
        'Opção': [],
        'Votos': [],
        'Data': []
    }

    for opcao, votos in st.session_state.votos.items():
        data['Opção'].append(opcao)
        data['Votos'].append(votos)
        data['Data'].append(now.strftime('%Y-%m-%d %H:%M:%S'))

    df = pd.DataFrame(data)
    df.to_csv('votos.csv', index=False)

# Função para filtrar os resultados por mês
def filtrar_por_mes(df, mes):
    if mes == 0:  # Se selecionar 'Todos'
        return df
    else:
        nome_mes = month_name[mes]  # Obter o nome do mês correspondente
        df['Data'] = pd.to_datetime(df['Data'])
        return df[df['Data'].dt.month == mes]

# Função para calcular indicadores
def calcular_indicadores(df):
    total_votos = df['Votos'].sum()
    if total_votos > 0:
        satisfeito = df[df['Opção'] == 'Satisfeito']['Votos'].sum()
        neutro = df[df['Opção'] == 'Neutro']['Votos'].sum()
        insatisfeito = df[df['Opção'] == 'Insatisfeito']['Votos'].sum()
    else:
        satisfeito = 0
        neutro = 0
        insatisfeito = 0
    
    return satisfeito, neutro, insatisfeito, total_votos

# Função para mostrar a tela principal
def tela_principal():
    st.markdown("""
        <style>
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .content {
            text-align: center;
        }
        .stButton button {
            width: 100px;
            height: 40px;
            font-size: 16px;
            font-weight: bold;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .footer-button {
            width: 150px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            height: 30px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .small-button {
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 5px;
            height: 25px;
            cursor: pointer;
            font-size: 12px;
            font-weight: bold;
            padding: 0 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title('Sistema de Feedback')
    st.markdown('<div class="content">', unsafe_allow_html=True)

    # Mostrar as carinhas e os botões de votação
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image('insatisfeito.png', width=100)
        if st.button('Insatisfeito', key='insatisfeito_button'):
            votar('Insatisfeito')

    with col2:
        st.image('neutro.png', width=100)
        if st.button('Neutro', key='neutro_button'):
            votar('Neutro')

    with col3:
        st.image('satisfeito.png', width=100)
        if st.button('Satisfeito', key='satisfeito_button'):
            votar('Satisfeito')

    st.markdown('</div>', unsafe_allow_html=True)

    # Espaço maior para posicionar o botão "Visualizar Relatórios" mais abaixo
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    # Botão invisível para controlar o fluxo da aplicação
    st.markdown('<div style="visibility: hidden;">', unsafe_allow_html=True)
    if st.button('Visualizar Relatórios', key='ver_relatorios_hidden'):
        st.session_state.page = 'resultados'
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Função para mostrar a tela de resultados
def tela_resultados():
    st.title('Resultados')

    # Carregar dados do arquivo votos.csv
    if os.path.exists('votos.csv'):
        df = pd.read_csv('votos.csv')
        df['Data'] = pd.to_datetime(df['Data'])
    else:
        df = pd.DataFrame(columns=['Opção', 'Votos', 'Data'])

    # Filtro por mês
    meses = ['Todos'] + list(month_name)[1:]
    mes_selecionado = st.selectbox('Filtrar por mês:', range(len(meses)), format_func=lambda x: meses[x])

    df_filtrado = filtrar_por_mes(df, mes_selecionado)

    # Mostrar tabela com resultados filtrados
    st.dataframe(df_filtrado, height=400)

    # Calcular e mostrar indicadores
    satisfeito, neutro, insatisfeito, total_votos = calcular_indicadores(df_filtrado)
    st.write('### Indicadores')
    st.write(f'Percentual de Satisfação: {satisfeito / total_votos * 100:.2f}%')
    st.write(f'Percentual de Neutro: {neutro / total_votos * 100:.2f}%')
    st.write(f'Percentual de Insatisfação: {insatisfeito / total_votos * 100:.2f}%')
    st.write(f'Total de Votos: {total_votos}')

    # Gráfico de quantidade de votos por opção
    st.write('### Quantidade de Votos por Opção')

    # Configuração das cores das barras
    colors = {'Satisfeito': 'lightgreen', 'Neutro': 'gold', 'Insatisfeito': 'lightcoral'}

    fig, ax = plt.subplots(figsize=(10, 6))

    if mes_selecionado == 0:  # Se selecionado 'Todos'
        sns.barplot(x='Opção', y='Votos', data=df, palette=colors, ax=ax)
    else:
        sns.barplot(x='Opção', y='Votos', data=df_filtrado, palette=colors, ax=ax)

    ax.set_xlabel('Opção')
    ax.set_ylabel('Quantidade de Votos')

    # Adicionar rótulos nos dados das barras
    if mes_selecionado == 0:  # Se selecionado 'Todos'
        for p in ax.patches:
            height = p.get_height()
            ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2, height),
                        ha='center', va='bottom', fontsize=12)

    ax.set_title('Quantidade de Votos por Opção')
    st.pyplot(fig)

    # Gráfico de percentual de votos por categoria
    st.write('### Percentual de Votos por Categoria')

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    labels = ['Satisfeito', 'Neutro', 'Insatisfeito']
    sizes = [satisfeito / total_votos * 100, neutro / total_votos * 100, insatisfeito / total_votos * 100]
    ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=['lightgreen', 'gold', 'lightcoral'])
    ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax2.set_title('Percentual de Votos por Categoria')
    st.pyplot(fig2)

# Definir layout da aplicação
def main():
    st.markdown('<style>body{background-color: #f5f5f5;}</style>', unsafe_allow_html=True)

    # Selecionar a página com base no botão clicado
    if 'page' not in st.session_state:
        st.session_state.page = 'principal'

    if st.session_state.page == 'principal':
        tela_principal()
    elif st.session_state.page == 'resultados':
        tela_resultados()

# Executar a aplicação
if __name__ == '__main__':
    main()

