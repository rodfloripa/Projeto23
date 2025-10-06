# Projeto23
Resoluçáo da prova da C&amp;A para o cargo de cientista de dados
Esta é uma pequena aplicação de chat inteligente, composta por dois
“sub-agentes”, que será consumida via API REST. O sistema mantem o histórico de
conversas em banco SQLite para simular um diálogo conHnuo. Um dos agentes vai tratar de
assuntos de SAC (políMcas de troca, devolução etc) e o outro agente vai tratar de buscar produtos
no catálogo da empresa.

Execute:
docker-compose up
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <ID do contêiner Milvus>

-Substitua no arquivo python o IP 172.18.0.4 pelo IP que obteve no comando anterior 
-Coloque o seu token da OpenAI no início do arquivo python 

-Instale as bibliotecas necessárias: pip install Requeriments.txt 
- Execute o script: 'python app.py'

Exemplo de uso

- `/sac`: Endpoint para responder às perguntas do SAC
    -  'curl -X POST -H "Content-Type: application/json" -d '{"pergunta": "Sua pergunta aqui"}' http://localhost:5000/sac'
- `/produtos`: Endpoint para buscar produtos
    -  'curl -X POST -H "Content-Type: application/json" -d '{"query": "Seu termo de busca aqui"}' http://localhost:5000/produtos'
