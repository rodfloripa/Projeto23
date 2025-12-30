import json
from flask import Flask, request, jsonify
from pymilvus import  DataType, connections
from pymilvus import Collection, FieldSchema, CollectionSchema
import openai,sqlite3
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
# Configuração da API da OpenAI
openai.api_key = "SUA_CHAVE_API_AQUI"

# Configuração do banco de dados vetorial
connections.connect(
    alias="default",
    host="milvus-standalone",
    port=19530,       
    user="root",       
    password="Milvus", 
    db_name="default",
    timeout=60)

# Criar banco de dados sql
conn = sqlite3.connect('conversas.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pergunta TEXT,
        resposta TEXT
    )
''')
conn.commit()

# Criar banco de dados vetorial
index_params = {
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024},
    "metric_type": "L2"
}



vector_field = FieldSchema(name="my_vector", dtype=DataType.FLOAT_VECTOR, dim=768)
id_field = FieldSchema(name="id_field", dtype=DataType.INT64, is_primary=True, description="Primary ID",auto_id=False)
pergunta = FieldSchema(name="pergunta", dtype=DataType.VARCHAR, max_length=2048)
resposta = FieldSchema(name="resposta", dtype=DataType.VARCHAR, max_length=2048)
schema = CollectionSchema(fields=[id_field, pergunta, resposta,vector_field], description="Milvus ")
collection = Collection(name="sac", schema=schema)
collection.create_index(field_name="my_vector", index_params=index_params)

# Carregar dados de SAC
dados_sac = {}
with open('dados-sac.md', 'r') as arquivo:
    linhas = arquivo.readlines()
    pergunta = None
    resposta = ''
    id = 1
    ids = []
    perguntas_list = []
    respostas_list = []
    vectors_list = []
    for linha in linhas:
        if linha.startswith('#'):   
            if pergunta:
                dados_sac[pergunta] = resposta.strip()
                vector = model.encode(pergunta)
                ids.append(id)
                perguntas_list.append(pergunta)
                respostas_list.append(resposta.strip())
                vectors_list.append(vector)
                collection.insert([
                ids,
                perguntas_list,
                respostas_list,
                vectors_list ])
                id += 1
            pergunta = linha[1:].strip()
            resposta = ''
        else:
            resposta += linha
    if pergunta:
        dados_sac[pergunta] = resposta.strip()
        vector = model.encode(pergunta)
        ids.append(id)
        perguntas_list.append(pergunta)
        respostas_list.append(resposta.strip())
        vectors_list.append(vector)
        collection.insert([
        ids,
        perguntas_list,
        respostas_list,
        vectors_list ])
        

# Carregar catalogo de produtos                             
with open('dados-produtos.json', 'r') as arquivo:
    catalogo_produtos = json.load(arquivo)

# Buscar produtos
    def buscar_produtos(query):
        resultados = []
        for produto in catalogo_produtos:
            if query.lower() in produto.get("title", "").lower():
                resultados.append(produto)
        return resultados

# Responder SAC
def responder_sac(pergunta):
    vector = model.encode(pergunta)
    collection.load()
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(data=[vector], anns_field="my_vector", param=search_params, limit=1, output_fields=["resposta"])
    if results[0].distances[0] < 1:
        return results[0].entity.get("resposta")
    else:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=pergunta,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()

# API
@app.route('/sac', methods=['POST'])
def sac():
    pergunta = request.get_json()["pergunta"]
    resposta = responder_sac(pergunta)
    cursor.execute('''INSERT INTO conversas (pergunta, resposta) VALUES (?, ?)''', (pergunta, resposta))
    conn.commit()
    return jsonify({"resposta": resposta})

@app.route('/produtos', methods=['POST'])
def produtos():
    query = request.get_json()["query"]
    resultados = buscar_produtos(query)
    return jsonify(resultados)

if __name__ == '__main__':
    try:
        app.run(host ="0.0.0.0", debug=False)
    finally:
        conn.close()



