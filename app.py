from flask import Flask, render_template, request, redirect, url_for
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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    print("Username:", conn.get_dsn_parameters()["user"])
    if request.method == "POST":
        table = request.form.get("table")
        print(table)
        if table:
            # Fetch data from the table
            def fetchData(table):
                cur = conn.cursor()
                cur.execute(f"SELECT * FROM {table}")
                return cur.fetchall()

            results = fetchData(table)

            return render_template("search_results.html", results=results, table=table)
        else:
            return render_template("search.html", error="Please enter a table")
    else:
        # Render the search form
        return render_template("search.html")

if __name__ == "__main__":
    app.run(debug=True)