from flask import Flask, render_template, request
import sqlite3
import json

app = Flask(__name__)

conn = sqlite3.connect('db/database.db', check_same_thread=False)
cursor = conn.cursor()

@app.route("/get_data", methods=["GET"])
def get_data():
    cursor.execute("SELECT * FROM test")
    data = cursor.fetchall()
    return json.dumps(data)

@app.route("/")
def statistics():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    query = """
        SELECT 
            u.user_name AS first_name,
            u.username,
            c.phone_number,
            u.created_at
        FROM user_info u
        LEFT JOIN contacts c ON u.user_id = c.user_id
        LIMIT ? OFFSET ?
    """
    cursor.execute(query, (per_page, offset))
    data = cursor.fetchall()

    total_rows = cursor.execute("SELECT COUNT(*) FROM user_info").fetchone()[0]
    total_pages = (total_rows + per_page - 1) // per_page

    # Получаем общее количество пользователей
    total_users_query = "SELECT COUNT(*) FROM user_info"
    total_users = cursor.execute(total_users_query).fetchone()[0]

    return render_template("statistics/statistics.html", data=data, page=page, total_pages=total_pages, total_users=total_users)

import datetime

@app.route("/statistics-week")
def statistics_week():
    today = datetime.date.today()

    one_week_ago = today - datetime.timedelta(days=7)

    cursor.execute("SELECT DATE(created_at) AS date, COUNT(*) AS count FROM user_info WHERE created_at >= ? GROUP BY date ORDER BY date ASC", (one_week_ago,))
    data = cursor.fetchall()

    labels = [row[0] for row in data]
    histogram_data = [row[1] for row in data]
    total_users = sum(row[1] for row in data)

    return render_template("statistics/statistics-week.html", data=data, labels=json.dumps(labels),
                           histogram_data=json.dumps(histogram_data), total_users=total_users)

@app.route("/statistics-month")
def statistics_month():
    today = datetime.date.today()

    one_month_ago = today - datetime.timedelta(days=30)

    cursor.execute("SELECT DATE(created_at) AS date, COUNT(*) AS count FROM user_info WHERE created_at >= ? GROUP BY date ORDER BY date ASC", (one_month_ago,))
    data = cursor.fetchall()

    labels = [row[0] for row in data]
    histogram_data = [row[1] for row in data]
    total_users = sum(row[1] for row in data)

    return render_template("statistics/statistics-week.html", data=data, labels=json.dumps(labels),
                           histogram_data=json.dumps(histogram_data), total_users=total_users)

@app.route("/test")
def test():
    cursor.execute("SELECT * FROM test")
    data = cursor.fetchall()

    labels = []
    histogram_data = []
    for row in data:
        labels.append(row[1])
        histogram_data.append(row[0])

    return render_template("test/test_results.html", data=data, labels=json.dumps(labels), histogram_data=json.dumps(histogram_data))

@app.route("/tools-change")
def tools_change():
    return render_template("tools/tools-change.html")

@app.route("/tools-add")
def tools_add():
    return render_template("tools/tools-add.html")

if __name__ == '__main__':
    app.run(debug=True)