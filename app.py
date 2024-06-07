from flask import Flask, render_template
import sqlite3
import json

app = Flask(__name__)

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()

@app.route("/")
def index():
    cursor.execute("SELECT * FROM user_info")
    data = cursor.fetchall()

    labels = []
    histogram_data = []
    for row in data:
        labels.append(row[1])
        histogram_data.append(row[0])

    total_users = len(data)

    return render_template("index.html", data=data, labels=json.dumps(labels),
                           histogram_data=json.dumps(histogram_data), total_users=total_users)
@app.route("/statistics")
def statistics():
    return render_template("statistics/statistics.html")

@app.route("/tools")
def tools():
    return render_template("tools/tools.html")

if __name__ == '__main__':
    app.run(debug=True)