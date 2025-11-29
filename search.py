# search.py
from flask import Flask, request, render_template
import psycopg2
from config.config import config

app = Flask(__name__)

# Connect to the database
conn = psycopg2.connect(
    host=config.db_host,
    port=config.db_port,
    database=config.db_name,
    user=config.db_user,
    password=config.db_password,
)

