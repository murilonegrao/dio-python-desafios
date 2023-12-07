from flask import Flask
import pandas as pd
import json

app = Flask(__name__)

@app.route('/')
def index():
    planilha = '/home/murilo-cpe/Documentos/Github/dio-python-desafios/app-flask/Planilha-flask - Página1.csv'
    dados = pd.read_csv(planilha)
    json_dados = dados.to_json(orient='records', indent=4)
    return json_dados

if __name__ == '__main__':
    app.run(debug=True)
