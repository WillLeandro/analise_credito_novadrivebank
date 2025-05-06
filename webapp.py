import streamlit as st
import requests
import yaml


st.title('Avaliação de Crédito')

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    url = config['url_api']['url']


profissao = ['Advogado', 'Arquiteto', 'Cientista de Dados','Contador', 'Dentista', 'Empresário', 'Engenheiro', 'Médico', 'Programador',  ]

tipo_residencia = ['Alugada', 'Própria', 'Outros']

escolaridade = ['Ens.Fundamental', 'Ens.Médio', 'PósouMais', 'Superior' ]

score = ['Baixo', 'Bom', 'Justo', 'MuitoBom']

estado_civil = ['Casado', 'Divorciado', 'Solteiro', 'Víuvo',  ]

produto = ['AgileXplorer', 'DoubleDuty', 'EcoPrestige',  'ElegantCruise', 'SpeedFury', 'TrailConqueror', 'VoyageRoamer', 'WorkMaster', ]


with st.form(key='prediction_form'):
    profissao = st.selectbox('Profissão', profissao )
    tempo_profissao = st.number_input('Tempo na profissão (em anos)', min_value=0, value=0 , step=1 )
    renda = st.number_input('Renda Mensal', min_value=0.0, value=0.0 , step=1000.0 )
    tipo_residencia = st.selectbox('Tipo de Residência', tipo_residencia )
    escolaridade = st.selectbox('Escolaridade', escolaridade )
    score = st.selectbox('Score', score )
    idade = st.number_input('Idade', min_value=18, max_value=110, value=25 , step=1 )
    dependentes = st.number_input('Dependentes', min_value=0, value=0 , step=1 )
    estado_civil = st.selectbox('Estado Civil', estado_civil )
    produto = st.selectbox('Produtos', produto )
    valor_solicitado = st.number_input('Valor Solicitado', min_value=0.0, value=0.0 , step=1000.0 )
    valor_total_bem = st.number_input('Valor total do Bem', min_value=0.0, value=0.0 , step=1000.0 )


    submit_button = st.form_submit_button(label='Consultar')

if submit_button:
    if valor_solicitado > 0:  # Evita divisão por zero
        proporcao = valor_total_bem / valor_solicitado
    else:
        proporcao = 0

    dados = {
        'profissao':[profissao],
        'tempoprofissao':[tempo_profissao],
        'renda':[renda],
        'tiporesidencia':[tipo_residencia],
        'escolaridade':[escolaridade],
        'score':[score],
        'idade':[idade],
        'dependentes':[dependentes],
        'estadocivil':[estado_civil],
        'produto':[produto],
        'valorsolicitado':[valor_solicitado],
        'valortotalbem':[valor_total_bem],
        'proporcao_solicitado_total': valor_total_bem / valor_solicitado        
    }

    response = requests.post( url, json=dados )

    if response.status_code == 200 :
        predictions = response.json()

        proba = predictions[0][0] * 100 # Converte para porcentagem
        classe = 'Bom' if proba > 50 else 'Ruim'

        st.success(f'Probalidade: {proba:.2f}%')
        st.success(f'Classe: {classe}')

    else:
        st.error(f'Erro ao fazer a previsão:{response.status_code}')






    

     