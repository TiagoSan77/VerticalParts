
from flask import Flask
from pymongo import MongoClient, errors
import os
from dotenv import load_dotenv


app = Flask(__name__)

# Carregar variáveis do .env
load_dotenv()

def connect():
    try:
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise Exception("Variável de ambiente MONGODB_URI não encontrada no .env")
        client = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000
        )
        client.server_info()
        print("✅ Conectado ao MongoDB com sucesso!")
        return client
    except errors.ServerSelectionTimeoutError as e:
        print("❌ Erro ao conectar ao MongoDB:", e)
        return None
    except Exception as e:
        print("❌ Erro de configuração:", e)
        return None