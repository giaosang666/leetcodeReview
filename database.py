import pymysql
from datetime import datetime, timedelta
import os
import json

CONFIG_FILE = 'db_config.json'

# 数据库连接
def connect_db():
    if not os.path.exists(CONFIG_FILE):
        create_config_file()
    
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    
    conn = pymysql.connect(
        host=config['host'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'problems'")
    result = cursor.fetchone()
    if not result:
        create_table(conn)
    return conn

def create_config_file():
    import getpass
    config = {
        'host': 'localhost',
        'user': input("Enter MySQL username: "),
        'password': getpass.getpass("Enter MySQL password: "),
        'database': 'leetcodereview'
    }
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS leetcodereview")
    cursor.execute("USE leetcodereview")
    cursor.execute("""
        CREATE TABLE problems (
            id INT AUTO_INCREMENT PRIMARY KEY,
            leetcode_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            difficulty VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            solve_date DATE NOT NULL,
            next_review DATE NOT NULL,
            review_count INT DEFAULT 0
        )
    """)
    conn.commit()

# 插入题目信息
def insert_problem(leetcode_id, title, difficulty, status, solve_date, next_review):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM problems WHERE leetcode_id = %s", (leetcode_id,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return False  # 题目已经存在
    cursor.execute(
        "INSERT INTO problems (leetcode_id, title, difficulty, status, solve_date, next_review) VALUES (%s, %s, %s, %s, %s, %s)",
        (leetcode_id, title, difficulty, status, solve_date, next_review)
    )
    conn.commit()
    conn.close()
    return True

# 计算下次复习时间
def calculate_next_review(solve_date, review_count):
    review_intervals = [1, 2, 3, 5, 7, 12, 20, 30]
    if review_count < len(review_intervals):
        return solve_date + timedelta(days=review_intervals[review_count])
    else:
        return solve_date + timedelta(days=review_intervals[-1])

# 获取今天需要复习的题目
def get_today_reviews():
    conn = connect_db()
    cursor = conn.cursor()
    today = datetime.now().date()
    cursor.execute("SELECT id, leetcode_id, title, difficulty, status FROM problems WHERE next_review <= %s", (today,))
    rows = cursor.fetchall()
    conn.close()
    return rows

# 更新题目复习状态
def update_review_status(problem_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT solve_date, review_count FROM problems WHERE id = %s", (problem_id,))
    solve_date, review_count = cursor.fetchone()
    next_review = calculate_next_review(solve_date, review_count + 1)
    cursor.execute(
        "UPDATE problems SET status = 'reviewed', review_count = review_count + 1, next_review = %s WHERE id = %s",
        (next_review, problem_id)
    )
    conn.commit()
    conn.close()

# 获取所有题目信息
def get_all_problems():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems")
    rows = cursor.fetchall()
    conn.close()
    return rows