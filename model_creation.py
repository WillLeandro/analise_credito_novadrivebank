import pandas as pandas
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import const
import joblib
from datetime import datetime
import random as python_random

from utils import *
from fuzzywuzzy import process
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
import tensorflow as tf

pd.options.mode.chained_assignment = None  # Silencia o warning de atribuição encadeada

seed = 42
np.random.seed(seed)
python_random.seed(seed)
tf.random.set_seed(seed)



## ======================================================
## 1. FUNÇÕES
## ======================================================

def trattar_nulos(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            moda = df[col].mode()[0]
            df.loc[:, col] = df[col].fillna(moda)
        else:
            median = df[col].median()
            df.loc[:, col] = df[col].fillna(median)
            
    return df
    

# Função para correção de erros de digitação
def corrigir_erros_digitacao(df, coluna, lista_valida):
    for i, valor in enumerate( df[coluna] ):
        valor_str = str(valor) if pd.notnull( valor ) else valor

        if valor_str not in lista_valida and pd.notnull( valor_str ):
            correcao = process.extractOne( valor_str, lista_valida )
            df.at[i, coluna ] = correcao


# Função para tratamento de Outiliers
def tratar_outliers( df, coluna, min_, max_ ):
    mediana = df [ ( df[coluna] >= min_) & ( df[coluna] <= max_) ][coluna].median()
    df[coluna] = df[coluna].apply( lambda x: mediana if x < min_ or x > max_ else x )
    return df


def save_scalers( df, nome_colunas):
    for nome_coluna in nome_colunas:
        scaler = StandardScaler()
        df[nome_coluna] = scaler.fit_transform( df[[nome_coluna]] )
        joblib.dump( scaler, f'./objetcs/scaler_{nome_coluna}.joblib' )

    return df

def save_label( df, nome_colunas):
    for nome_coluna in nome_colunas:
        label_encoder = LabelEncoder()
        df[nome_coluna] = label_encoder.fit_transform( df[nome_coluna] )
        joblib.dump( label_encoder, f'./objetcs/label_{nome_coluna}.joblib' )

    return df

def save_onehot( df, nome_colunas):
    for nome_coluna in nome_colunas:
        one_hot = OneHotEncoder()
        df[nome_coluna] = one_hot.fit_transform( df[[nome_coluna]] )
        joblib.dump( one_hot, f'./objetcs/onehot_{nome_coluna}.joblib' )

    return df

## ======================================================
## 2. CARREGAMENTO DOS DADOS
## ======================================================

df = fetch_data_from_db(const.consulta_sql)


## ======================================================
## 3. TRATAMENTO DOS DADOS
## ======================================================

df1 = df.copy()

df1['idade'] = df1['idade'].astype(int)
df1['valorsolicitado'] = df1['valorsolicitado'].astype(float)
df1['valortotalbem'] = df1['valortotalbem'].astype(float)

# Trantamento de Dados Nulos
trattar_nulos(df1)

# Tratamento de erros de digitação
profissoes_validas = ['Advogado', 'Arquiteto','Cientista de Dados','Contador','Dentista', 'Empresário','Engenheiro','Médico','Prgramador']

corrigir_erros_digitacao( df1, 'profissao', profissoes_validas )

# Tratamento de Outiliers
df1 = tratar_outliers( df1, 'tempoprofissao', 0, 70 )
df1 = tratar_outliers( df1, 'idade', 0, 100 )

## =====================================================
## 4. ENGENHARIA DE FEATURES
## =====================================================

df1['proporcao_solicitado_total'] = df1['valorsolicitado'] / df1['valortotalbem']
df1['proporcao_solicitado_total'] = df1['proporcao_solicitado_total'].astype(float)

## =====================================================
## 5. SEPARAÇÃO DOS DADOS EM TREINO E TESTE
## =====================================================

X = df1.drop('classe', axis=1)
y = df1['classe']

X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.2, random_state=seed )

## =====================================================
## 6. NORMALIZAÇÃO DOS DADOS
## =====================================================

X_test = save_scalers( X_test, ['tempoprofissao','renda','idade','dependentes','valorsolicitado','valortotalbem','proporcao_solicitado_total'])

X_train = save_scalers( X_train, ['tempoprofissao','renda','idade','dependentes','valorsolicitado','valortotalbem','proporcao_solicitado_total'])

## =====================================================
## 7. ENCODINF DOS DADOS CATEGÓRICOS
## =====================================================

map_ = {'Ruim': 0, 'Bom': 1 }

for col in ['profissao', 'tiporesidencia', 'escolaridade', 'score', 'estadocivil', 'produto']:
    X_train[col] = X_train[col].astype(str)
    X_test[col] = X_test[col].astype(str)


y_train = np.array( [ map_[item] for item in y_train ] )
y_test = np.array( [ map_[item] for item in y_test ] )

X_train = save_label( X_train, ['profissao','tiporesidencia','escolaridade','score','estadocivil','produto'])
X_test  = save_label( X_test,  ['profissao','tiporesidencia','escolaridade','score','estadocivil','produto'])

## =====================================================
## 8. SELEÇÃO DE FEATURES
## =====================================================


model = RandomForestClassifier()

selector = RFE(model, n_features_to_select=10, step=1)
selector = selector.fit(X_train, y_train)

X_train = selector.transform(X_train)
X_test = selector.transform(X_test)

joblib.dump(selector,'./objetcs/selector.joblib')

print(selector.support_)
print(selector.ranking_)

## =====================================================
## 9. TREINAMENTO DO MODELO
## =====================================================

model = tf.keras.Sequential([
    tf.keras.layers.Dense( 128, activation='relu', input_shape=(X_train.shape[1],)),
    # tf.keras.layers.Dense(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    # tf.keras.layers.Dense(0.3),
    tf.keras.layers.Dense(32, activation='relu'),
    # tf.keras.layers.Dense(0.3),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Configurando o otimizado
optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)

# Compilando o modelo
model.compile(optimizer=optimizer, loss= 'binary_crossentropy', metrics=['accuracy'])

# Treinamento do modelo
model.fit(
    X_train,
    y_train,
    validation_split=0.2,
    epochs=500,
    batch_size=10,
    verbose=1
)

model.save('meu_modelo.keras')

# Previsões
y_pred = model.predict( X_test)
y_pred = ( y_pred > 0.5).astype(int)

# Avaliando o modelo
print('Avaliação do Modelo nos Dados de Teste')
model.evaluate( X_test, y_test)

# Métricas de Classificação
print('\nRelatório de Classificação')
print(classification_report( y_test, y_pred) )


