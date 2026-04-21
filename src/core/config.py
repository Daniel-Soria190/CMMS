import os
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv('SERVER')
PORT = os.getenv("PORT")
DBUSER = os.getenv('DBUSER')
PASSWORD = os.getenv('PASSWORD')
DATABASE = os.getenv('DATABASE')