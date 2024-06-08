from flask import Flask, render_template
import sqlite3
import json

app = Flask(__name__)

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()

@app.route("/")
def statistics():
    cursor.execute("SELECT * FROM user_info")
    data = cursor.fetchall()

    labels = []
    histogram_data = []
    for row in data:
        labels.append(row[1])
        histogram_data.append(row[0])

    total_users = len(data)

    return render_template("statistics/statistics.html", data=data, labels=json.dumps(labels),
                           histogram_data=json.dumps(histogram_data), total_users=total_users)

@app.route("/statistics")
def statistics():
    cursor.execute("SELECT * FROM user_info")
    data = cursor.fetchall()

    labels = []
    histogram_data = []
    for row in data:
        labels.append(row[1])
        histogram_data.append(row[0])

    total_users = len(data)

    return render_template("statistics/statistics-day.html", data=data, labels=json.dumps(labels),
                           histogram_data=json.dumps(histogram_data), total_users=total_users)

@app.route("/statistics")
def statistics():
    cursor.execute("SELECT * FROM user_info")
    data = cursor.fetchall()

    labels = []
    histogram_data = []
    for row in data:
        labels.append(row[1])
        histogram_data.append(row[0])

    total_users = len(data)

    return render_template("statistics/statistics-week.html", data=data, labels=json.dumps(labels),
                           histogram_data=json.dumps(histogram_data), total_users=total_users)

@app.route("/statistics")
def statistics():
    cursor.execute("SELECT * FROM user_info")
    data = cursor.fetchall()

    labels = []
    histogram_data = []
    for row in data:
        labels.append(row[1])
        histogram_data.append(row[0])

    total_users = len(data)

    return render_template("statistics/statistics-month.html", data=data, labels=json.dumps(labels),
                           histogram_data=json.dumps(histogram_data), total_users=total_users)

@app.route("/tools")
def tools():
    return render_template("tools/tools-change.html")

@app.route("/tools")
def tools():
    return render_template("tools/tools-add.html")

if __name__ == '__main__':
    app.run(debug=True)