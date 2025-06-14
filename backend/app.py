from flask import Flask, request, jsonify, g
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
import database

app = Flask(__name__)
CORS(app)


# 辅助函数：判断任务是否在指定日期活跃（考虑 start_date, end_date, recurrence_days）
def is_task_scheduled_for_date(task, target_date_obj):
    task_start_date_obj = datetime.strptime(task['start_date'], '%Y-%m-%d').date()

    if task_start_date_obj > target_date_obj:
        return False

    task_end_date_str = task.get('end_date')
    if task_end_date_str:
        try:
            task_end_date_obj = datetime.strptime(task_end_date_str, '%Y-%m-%d').date()
            if target_date_obj > task_end_date_obj:
                return False
        except ValueError:
            print(f"Warning: Invalid end_date format for task {task.get('id', 'N/A')}: {task_end_date_str}")
            return False

    recurrence_days_str = task['recurrence_days']
    try:
        recurrence_list = [int(d.strip()) for d in recurrence_days_str.split(',') if d.strip()]
    except ValueError:
        print(f"Warning: Invalid recurrence_days format for task {task.get('id', 'N/A')}: {recurrence_days_str}")
        return False

    if target_date_obj.weekday() in recurrence_list:
        return True

    return False


# 新的辅助函数：计算单个任务的完成率
def calculate_single_task_completion_rate(task_id, task_info, cursor):
    scheduled_days_count = 0
    completed_count = 0

    task_start_date_obj = datetime.strptime(task_info['start_date'], '%Y-%m-%d').date()

    today_date_obj = datetime.now().date()

    current_date_iter = task_start_date_obj
    while current_date_iter <= today_date_obj:
        if is_task_scheduled_for_date(task_info, current_date_iter):
            scheduled_days_count += 1
            completion_status = cursor.execute(
                'SELECT is_completed FROM daily_completions WHERE task_id = ? AND date = ?',
                (task_id, current_date_iter.strftime('%Y-%m-%d'))
            ).fetchone()
            if completion_status and completion_status['is_completed']:
                completed_count += 1
        current_date_iter += timedelta(days=1)

    return f"{(completed_count / scheduled_days_count * 100):.1f}" if scheduled_days_count > 0 else "0.0"


# 每次请求前连接数据库
@app.before_request
def before_request():
    g.db = database.get_db_connection()


# 每次请求后关闭数据库连接
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


# 初始化数据库
database.init_db()


# --- 任务管理 API ---

# 获取所有活跃任务 (带完成率)
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    cursor = g.db.cursor()
    tasks_raw = cursor.execute(
        'SELECT id, name, is_active, start_date, end_date, recurrence_days FROM tasks WHERE is_active = 1 ORDER BY created_at DESC').fetchall()

    tasks_with_stats = []
    for task_row in tasks_raw:
        task = dict(task_row)
        task['completion_rate'] = calculate_single_task_completion_rate(task['id'], task, cursor)
        tasks_with_stats.append(task)

    return jsonify(tasks_with_stats)


# 获取单个任务的详细信息 (带完成率)
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_single_task(task_id):
    cursor = g.db.cursor()
    task_row = cursor.execute(
        'SELECT id, name, is_active, start_date, end_date, recurrence_days, created_at FROM tasks WHERE id = ?',
        (task_id,)
    ).fetchone()

    if task_row is None:
        return jsonify({'error': 'Task not found'}), 404

    task_info = dict(task_row)
    task_info['completion_rate'] = calculate_single_task_completion_rate(task_info['id'], task_info, cursor)

    # 可以在这里添加更多未来可能需要的指标
    # task_info['some_other_metric'] = calculate_some_other_metric(...)

    return jsonify(task_info)


@app.route('/api/tasks', methods=['POST'])
def add_task():
    name = request.json.get('name')
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')
    recurrence_days = request.json.get('recurrence_days')

    if not name:
        return jsonify({'error': 'Task name is required'}), 400
    if not start_date:
        start_date = datetime.now().strftime('%Y-%m-%d')
    if not recurrence_days:
        recurrence_days = '0,1,2,3,4,5,6'

    try:
        cursor = g.db.cursor()
        cursor.execute(
            'INSERT INTO tasks (name, start_date, end_date, recurrence_days) VALUES (?, ?, ?, ?)',
            (name, start_date, end_date, recurrence_days)
        )
        g.db.commit()
        return jsonify({'message': 'Task added successfully', 'id': cursor.lastrowid}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Task with this name already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    name = data.get('name')
    is_active = data.get('is_active')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    recurrence_days = data.get('recurrence_days')

    if not any([name, is_active is not None, start_date, end_date is not None, recurrence_days]):
        return jsonify({'error': 'No data provided for update'}), 400

    update_fields = []
    update_values = []

    if name is not None:
        update_fields.append('name = ?')
        update_values.append(name)
    if is_active is not None:
        update_fields.append('is_active = ?')
        update_values.append(int(is_active))
    if start_date is not None:
        update_fields.append('start_date = ?')
        update_values.append(start_date)
    if end_date is not None:
        update_fields.append('end_date = ?')
        update_values.append(end_date)
    if recurrence_days is not None:
        update_fields.append('recurrence_days = ?')
        update_values.append(recurrence_days)

    if not update_fields:
        return jsonify({'error': 'Invalid update data'}), 400

    update_values.append(task_id)

    try:
        cursor = g.db.cursor()
        cursor.execute(f'UPDATE tasks SET {", ".join(update_fields)} WHERE id = ?', tuple(update_values))
        g.db.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify({'message': 'Task updated successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Task with this name already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        cursor = g.db.cursor()
        cursor.execute('UPDATE tasks SET is_active = 0 WHERE id = ?', (task_id,))
        g.db.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify({'message': 'Task marked as inactive'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- 完成情况管理 API (这些路由不需要改变，因为它们调用了 is_task_scheduled_for_date) ---

@app.route('/api/completions/<string:date_str>', methods=['GET'])
def get_daily_completions(date_str):
    cursor = g.db.cursor()
    target_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

    all_active_tasks_raw = cursor.execute(
        'SELECT id, name, start_date, end_date, recurrence_days FROM tasks WHERE is_active = 1').fetchall()

    scheduled_tasks = []
    for task_row in all_active_tasks_raw:
        task_info = dict(task_row)
        if is_task_scheduled_for_date(task_info, target_date_obj):
            scheduled_tasks.append(task_info)

    completed_status = {}
    if scheduled_tasks:
        scheduled_task_ids = [t['id'] for t in scheduled_tasks]
        if scheduled_task_ids:  # 确保列表不为空
            placeholders = ','.join(['?' for _ in scheduled_task_ids])
            completed_tasks_raw = cursor.execute(
                f'SELECT task_id, is_completed FROM daily_completions WHERE date = ? AND task_id IN ({placeholders})',
                (date_str, *scheduled_task_ids)
            ).fetchall()
            completed_status = {row['task_id']: bool(row['is_completed']) for row in completed_tasks_raw}

    result = []
    for task in scheduled_tasks:
        task_info = dict(task)
        task_info['is_completed_today'] = completed_status.get(task['id'], False)
        result.append(task_info)

    return jsonify(result)


@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    task_id = request.json.get('task_id')
    date_str = request.json.get('date')
    is_completed = request.json.get('is_completed')

    if not all([task_id, date_str is not None, is_completed is not None]):
        return jsonify({'error': 'Missing task_id, date, or is_completed'}), 400

    try:
        cursor = g.db.cursor()
        cursor.execute('''
            INSERT INTO daily_completions (task_id, date, is_completed, completed_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(task_id, date) DO UPDATE SET
                is_completed = EXCLUDED.is_completed,
                completed_at = CURRENT_TIMESTAMP
        ''', (task_id, date_str, int(is_completed)))
        g.db.commit()
        return jsonify({'message': 'Completion status updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    cursor = g.db.cursor()
    today = datetime.now().date()

    all_active_tasks_raw = cursor.execute(
        'SELECT id, name, start_date, end_date, recurrence_days FROM tasks WHERE is_active = 1').fetchall()
    all_active_task_map = {task['id']: dict(task) for task in all_active_tasks_raw}

    history_data_by_date = {}

    for i in range(30):  # 最近30天
        current_date_obj = today - timedelta(days=i)
        date_str = current_date_obj.strftime('%Y-%m-%d')

        scheduled_tasks_today = []
        for task_id, task_info in all_active_task_map.items():
            if is_task_scheduled_for_date(task_info, current_date_obj):
                scheduled_tasks_today.append(task_info)

        total_scheduled_tasks = len(scheduled_tasks_today)
        completed_count_today = 0
        tasks_status_list = []

        completions_for_date_raw = cursor.execute(
            'SELECT task_id, is_completed FROM daily_completions WHERE date = ?',
            (date_str,)
        ).fetchall()
        completions_map_for_date = {row['task_id']: bool(row['is_completed']) for row in completions_for_date_raw}

        for task_info in scheduled_tasks_today:
            is_completed = completions_map_for_date.get(task_info['id'], False)
            if is_completed:
                completed_count_today += 1
            tasks_status_list.append({
                'task_id': task_info['id'],
                'task_name': task_info['name'],
                'is_completed': is_completed
            })

        history_data_by_date[date_str] = {
            'date': date_str,
            'total_active_tasks': total_scheduled_tasks,
            'completed_count': completed_count_today,
            'tasks_status': sorted(tasks_status_list, key=lambda x: x['task_name'])
        }

    sorted_history = sorted(
        history_data_by_date.values(),
        key=lambda x: x['date'],
        reverse=True
    )

    return jsonify(sorted_history)


if __name__ == '__main__':
    app.run(debug=True, port=5001)