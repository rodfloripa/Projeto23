FROM python:3.9-slim

# Definir diretório de trabalho
WORKDIR /usr/app

# Instalar dependências do sistema necessárias para bibliotecas Python (como o Milvus/Transformers)
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Atualizar pip e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY . .

# Comando para rodar a aplicação Flask
CMD ["python", "app.py"]
