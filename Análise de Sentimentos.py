import pandas as pd
import gspread
from google.colab import auth
from google.auth import default
from transformers import pipeline
from openai import OpenAI
import requests

# Autenticação no Google Colab
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)

# Abrir a planilha pelo URL
sheet = gc.open_by_url('LINK_DA_PLANILHA').sheet1

# Carregar dados em um DataFrame
df = pd.DataFrame(sheet.get_all_records())

# Configurar a chave da API do OpenAI
api_key = 'API_TOKEN'

# Função para classificar o sentimento do comentário
def classify_comment(comment):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Você é um assistente que classifica comentários como 'Positivo' ou 'Negativo'."},
            {"role": "user", "content": f"Classifique o seguinte comentário como 'Positivo' ou 'Negativo': {comment}"}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    # Verificar se a resposta contém a chave 'choices'
    if 'choices' in response_data:
        sentiment = response_data['choices'][0]['message']['content'].strip()
        return sentiment
    else:
        # Imprimir a resposta completa para depuração
        print(f"Erro na resposta da API: {response_data}")
        return "Erro na classificação"

# Aplicar a classificação aos comentários
df['Classificação'] = df['Comentários'].apply(classify_comment)

# Atualizar a planilha com as classificações
# Encontrar a coluna "Classificação" no Google Sheets
header_row = sheet.row_values(1)
classificacao_col_idx = header_row.index('Classificação') + 1

for i, classification in enumerate(df['Classificação']):
    # Atualizar a célula correspondente na coluna "Classificação"
    sheet.update_cell(i + 2, classificacao_col_idx, classification)

# Exibir a classificação
print(df)
