import os
import psycopg
from dotenv import load_dotenv

load_dotenv()  # lit le fichier .env

def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5432,
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )
