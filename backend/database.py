import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'mytasks.db')


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 创建 tasks 表
    # 新增 end_date 字段
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            is_active BOOLEAN NOT NULL DEFAULT 1, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            start_date TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d', 'now')), -- YYYY-MM-DD 格式
            end_date TEXT NULL, -- 新增：YYYY-MM-DD 格式，可以是 NULL 表示没有结束日期
            recurrence_days TEXT NOT NULL DEFAULT '0,1,2,3,4,5,6' -- 逗号分隔的周几数字 (0-6, 周日-周六)
        )
    ''')

    # daily_completions 表保持不变
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            date TEXT NOT NULL, -- YYYY-MM-DD 格式
            is_completed BOOLEAN NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')

    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_task_date ON daily_completions (task_id, date)
    ''')

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == '__main__':
    init_db()
    print(f"Database initialized at: {DATABASE_PATH}")