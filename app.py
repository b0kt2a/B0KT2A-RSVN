from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta
import re  # 이거 추가해야 돼!

app = Flask(__name__)

# 🔗 링크에 target="_blank" 자동 추가하는 함수
def add_target_blank(html):
    return re.sub(r'<a\s+(?![^>]*target)', r'<a target="_blank" ', html)

@app.route('/', methods=['GET', 'POST'])
def index():
    reservation_results = []
    selected_date = ''
    selected_store = ''
    stores = []

    # 자동완성용 매장 리스트 불러오기
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
            SELECT name, deadline_days, deadline_time, always_open, fixed_note, memo
            FROM stores
            WHERE keywords LIKE ?
        ''', (f'%{selected_store}%',))
        results = cursor.fetchall()
        conn.close()

        for name, deadline_days, deadline_time, always_open, fixed_note, memo in results:
            if always_open and int(always_open) == 1:
                deadline = fixed_note if fixed_note else '상시 예약 가능'
            elif deadline_days is not None and deadline_time:
                selected = datetime.strptime(selected_date, '%Y-%m-%d')
                deadline_date = selected - timedelta(days=int(deadline_days))
                deadline = deadline_date.strftime('%Y년 %m월 %d일 ') + deadline_time
            else:
                deadline = fixed_note if fixed_note else '정보 없음'

            # ✨ memo에 target="_blank" 자동 삽입
            if memo:
                memo = add_target_blank(memo)

            reservation_results.append({
                'name': name,
                'deadline': deadline,
                'memo': memo
            })

    return render_template('index.html',
                           stores=stores,
                           reservation_results=reservation_results,
                           selected_date=selected_date,
                           selected_store=selected_store)

if __name__ == '__main__':
    app.run(debug=True)
