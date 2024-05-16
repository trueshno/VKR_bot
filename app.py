from flask import Flask, render_template
import sqlite3
import json

app = Flask(__name__)

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()

@app.route("/")
def index():
    cursor.execute("SELECT * FROM test")
    data = cursor.fetchall()

    labels = []
    histogram_data = []
    for row in data:
        labels.append(row[1])
        histogram_data.append(row[0])

    return render_template("index.html", data=data, labels=json.dumps(labels), histogram_data=json.dumps(histogram_data))

@app.route("/statistics")
def statistics():
    # Логика обработки запроса для страницы "Статистика"
    return render_template("statistics.html")

@app.route("/tools")
def tools():
    # Логика обработки запроса для страницы "Инструменты"
    return render_template("tools/tools.html")

if __name__ == '__main__':
    app.run(debug=True)