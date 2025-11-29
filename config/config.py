from dotenv import load_dotenv
import os

class Config:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "new_schema")
        self.db_user = os.getenv("DB_USER", "root")
        self.db_password = os.getenv("DB_PASSWORD", "")

config = Config()