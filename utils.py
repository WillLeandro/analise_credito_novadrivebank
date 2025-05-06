import pandas as pd
import joblib
import yaml
import psycopg2

from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder

def fetch_data_from_db(sql_query):

    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        con = psycopg2.connect(
            dbname=config['database_config']['dbname'],
            user=config['database_config']['user'],
            password=config['database_config']['password'],
            host=config['database_config']['host']
        )

        cursor = con.cursor()
        cursor.execute(sql_query)

        df = pd.DataFrame(cursor.fetchall(), columns=[ desc[0] for desc in cursor.description] )

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close

    return df

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

# Função para carregar os scalers e label encoders

def load_scaler(df, nome_colunas):
    for nome_coluna in nome_colunas:
        nome_coluna_arquivo_scaler = fr'./objetcs/scaler_{nome_coluna}.joblib'
        scaler = joblib.load(nome_coluna_arquivo_scaler)
        df[nome_coluna] = scaler.transform( df[[nome_coluna]])
    
    return df

def load_label(df, nome_colunas):
    for nome_coluna in nome_colunas:
        nome_coluna_arquivo_label = fr'./objetcs/label_{nome_coluna}.joblib'
        label = joblib.load(nome_coluna_arquivo_label)
        df[nome_coluna] = label.transform( df[nome_coluna])
    
    return df
    