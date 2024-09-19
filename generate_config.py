import json
import os
import mysql.connector
from tkinter import simpledialog
import ttkbootstrap as ttk

CONFIG_FILE = 'db_config.json'

def create_database_and_table(host, user, password, database):
    try:
        # 连接到MySQL服务器
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = conn.cursor()

        # 创建数据库
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        cursor.execute(f"USE {database}")

        # 创建表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INT AUTO_INCREMENT PRIMARY KEY,
            leetcode_id VARCHAR(10),
            title VARCHAR(255),
            difficulty ENUM('easy', 'medium', 'hard'),
            status ENUM('solved', 'reviewed'),
            solve_date DATE,
            next_review DATE
        )
        """)

        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_database_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    
    root = ttk.Window()
    root.withdraw()  # 隐藏主窗口

    config = {}
    config['host'] = simpledialog.askstring("Database Configuration", "Enter MySQL host:", initialvalue="localhost")
    config['user'] = simpledialog.askstring("Database Configuration", "Enter MySQL username:")
    config['password'] = simpledialog.askstring("Database Configuration", "Enter MySQL password:", show='*')
    config['database'] = simpledialog.askstring("Database Configuration", "Enter database name:", initialvalue="leetcode_app")

    if all(config.values()):
        if create_database_and_table(**config):
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)
            return config
    
    return None

if __name__ == "__main__":
    config = get_database_config()
    if config:
        print("Database configuration successful.")
    else:
        print("Database configuration failed.")