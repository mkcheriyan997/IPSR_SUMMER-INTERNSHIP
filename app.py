import os
import sqlite3
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)
DB_FILE = 'todo.db'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Initialize DB on startup
init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern To-Do App</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            background: radial-gradient(circle at 50% 50%, #1e1e38 0%, #0d0d1a 100%);
            color: #f1f5f9;
            font-family: 'Outfit', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .todo-container {
            background: rgba(30, 41, 59, 0.45);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 28px;
            padding: 40px;
            width: 100%;
            max-width: 500px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            transition: all 0.3s ease;
        }
        .todo-header {
            font-size: 2.2rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 8px;
            background: linear-gradient(to right, #818cf8, #c084fc, #f472b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }
        .todo-subtitle {
            font-size: 0.95rem;
            color: #94a3b8;
            text-align: center;
            margin-bottom: 30px;
            font-weight: 400;
        }
        .todo-form {
            display: flex;
            gap: 12px;
            margin-bottom: 25px;
        }
        .todo-input {
            flex: 1;
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            padding: 15px 20px;
            color: #ffffff;
            font-size: 1rem;
            font-family: inherit;
            outline: none;
            transition: all 0.3s ease;
        }
        .todo-input::placeholder {
            color: #64748b;
        }
        .todo-input:focus {
            border-color: #818cf8;
            box-shadow: 0 0 15px rgba(129, 140, 248, 0.35);
            background: rgba(15, 23, 42, 0.7);
        }
        .todo-btn {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            color: #ffffff;
            border: none;
            border-radius: 14px;
            padding: 15px 24px;
            font-size: 1rem;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .todo-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5);
            background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%);
        }
        .todo-btn:active {
            transform: translateY(0);
        }
        .task-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 12px;
            max-height: 380px;
            overflow-y: auto;
            padding-right: 4px;
        }
        /* Custom scrollbar for task list */
        .task-list::-webkit-scrollbar {
            width: 6px;
        }
        .task-list::-webkit-scrollbar-track {
            background: transparent;
        }
        .task-list::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }
        .task-list::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        .task-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(30, 41, 59, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 16px;
            padding: 16px 20px;
            transition: all 0.3s ease;
        }
        .task-item:hover {
            background: rgba(30, 41, 59, 0.55);
            border-color: rgba(129, 140, 248, 0.25);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .task-content {
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
        }
        .task-title {
            font-size: 1.05rem;
            font-weight: 400;
            color: #e2e8f0;
            transition: all 0.3s ease;
            word-break: break-all;
        }
        .task-item.completed {
            background: rgba(30, 41, 59, 0.15);
            border-color: rgba(255, 255, 255, 0.02);
        }
        .task-item.completed .task-title {
            text-decoration: line-through;
            color: #64748b;
        }
        /* Custom toggle form button instead of basic checkbox */
        .toggle-form {
            display: inline-flex;
        }
        .toggle-btn {
            background: none;
            border: none;
            cursor: pointer;
            padding: 0;
            color: #64748b;
            font-size: 1.3rem;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .toggle-btn:hover {
            color: #818cf8;
        }
        .task-item.completed .toggle-btn {
            color: #10b981;
        }
        /* Delete form / button */
        .delete-form {
            display: inline-flex;
        }
        .delete-btn {
            background: none;
            border: none;
            color: #64748b;
            cursor: pointer;
            padding: 8px;
            border-radius: 10px;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.95rem;
        }
        .delete-btn:hover {
            color: #ef4444;
            background: rgba(239, 68, 68, 0.12);
        }
        .empty-state {
            text-align: center;
            color: #64748b;
            font-size: 1rem;
            padding: 40px 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }
        .empty-state i {
            font-size: 2.5rem;
            background: linear-gradient(to bottom, #475569, #334155);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
</head>
<body>
    <div class="todo-container">
        <h1 class="todo-header">Task Hub</h1>
        <p class="todo-subtitle">Stay organized and get things done</p>
        
        <form class="todo-form" action="/add" method="POST">
            <input class="todo-input" type="text" name="title" placeholder="Add a new task..." required autocomplete="off">
            <button class="todo-btn" type="submit">
                <i class="fa-solid fa-plus"></i> Add
            </button>
        </form>
        
        <ul class="task-list">
            {% for task in tasks %}
            <li class="task-item {% if task.completed %}completed{% endif %}">
                <div class="task-content">
                    <form class="toggle-form" action="/toggle/{{ task.id }}" method="POST">
                        <button type="submit" class="toggle-btn" title="Toggle complete">
                            {% if task.completed %}
                            <i class="fa-solid fa-circle-check"></i>
                            {% else: %}
                            <i class="fa-regular fa-circle"></i>
                            {% endif %}
                        </button>
                    </form>
                    <span class="task-title">{{ task.title }}</span>
                </div>
                <form class="delete-form" action="/delete/{{ task.id }}" method="POST">
                    <button type="submit" class="delete-btn" title="Delete task">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </form>
            </li>
            {% else %}
            <div class="empty-state">
                <i class="fa-solid fa-list-check"></i>
                <p>No tasks yet. Create one to get started!</p>
            </div>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title', '').strip()
    if title:
        conn = get_db()
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>', methods=['POST'])
def toggle(task_id):
    conn = get_db()
    cursor = conn.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if row:
        new_status = 1 if row['completed'] == 0 else 0
        conn.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
        conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
