from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

def connectToPostgres():
    load_dotenv()
    connection_string = os.getenv("DATABASE_URL")
    engine = create_engine(connection_string)
    return engine


