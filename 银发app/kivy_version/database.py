import sqlite3
import os

def init_database():
    """初始化数据库，创建必要的表结构"""
    try:
        # 连接数据库
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # 创建管理员表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建菜品表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image_url TEXT,
            category TEXT,
            is_available INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建社区通知表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
        ''')
        
        # 创建用户地址表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            contact_name TEXT DEFAULT '本人',
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 提交更改
        conn.commit()
        
        # 检查是否需要添加默认管理员账号
        cursor.execute('SELECT COUNT(*) FROM admins')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # 添加默认管理员账号（密码：pdsu）
            cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', ('admin', 'pdsu'))
            conn.commit()
            print("默认管理员账号已创建: admin/pdsu")
        
        # 关闭连接
        conn.close()
        print("数据库初始化成功")
        return True
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect('data.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"获取数据库连接失败: {e}")
        return None

def close_db_connection(conn):
    """关闭数据库连接"""
    if conn:
        try:
            conn.close()
        except Exception as e:
            print(f"关闭数据库连接失败: {e}")

# 测试数据库初始化
if __name__ == "__main__":
    init_database()
