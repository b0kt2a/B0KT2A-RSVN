from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    reservation_results = []
    selected_date = ''
    selected_store = ''
    stores = []

    # 자동완성용 매장 리스트
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM stores")
    stores = [row[0] for row in cursor.fetchall()]
    conn.close()

    if request.method == 'POST':
        selected_date = request.form['date']
        selected_store = request.form['store'].strip()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name, deadline_days, deadline_time FROM stores
            WHERE name LIKE ? OR keywords LIKE ?
        ''', (f'%{selected_store}%', f'%{selected_store}%'))
        results = cursor.fetchall()
        conn.close()

        if results:
            for name, deadline_days, deadline_time in results:
                selected = datetime.strptime(selected_date, '%Y-%m-%d')
                deadline_date = selected - timedelta(days=deadline_days)
                reservation_deadline = deadline_date.strftime('%Y년 %m월 %d일 ') + deadline_time
                reservation_results.append({
                    'name': name,
                    'deadline': reservation_deadline
                })
        else:
            reservation_results = []

    return render_template('index.html',
                           stores=stores,
                           reservation_results=reservation_results,
                           selected_date=selected_date,
                           selected_store=selected_store)

if __name__ == '__main__':
    app.run(debug=True)
