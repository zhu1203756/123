import sqlite3
from pathlib import Path
from datetime import datetime
from kivy.utils import platform
import os

class DatabaseManager:
    def __init__(self):
        self.db_path = self.get_db_path()
        self.init_database()
    
    def get_db_path(self):
        """根据平台获取数据库路径"""
        if platform == 'android':
            # Android 平台使用外部存储
            from jnius import autoclass
            Environment = autoclass('android.os.Environment')
            DocumentDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS)
            return os.path.join(str(DocumentDir), 'silverhair.db')
        else:
            # 桌面平台使用当前目录
            return os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')
    
    def get_connection(self):
        """获取数据库连接"""
        # 确保目录存在
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 先创建表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                record_type TEXT,
                value TEXT,
                unit TEXT,
                note TEXT,
                record_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 检查value字段类型，如果是REAL则修改为TEXT
        try:
            # 获取表结构
            cursor.execute("PRAGMA table_info(health_records)")
            columns = cursor.fetchall()
            
            # 查找value列
            for column in columns:
                if column[1] == 'value' and column[2] == 'REAL':
                    # 创建临时表
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS health_records_temp (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            record_type TEXT,
                            value TEXT,
                            unit TEXT,
                            note TEXT,
                            record_time DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # 复制数据到临时表
                    cursor.execute('''
                        INSERT INTO health_records_temp (id, user_id, record_type, value, unit, note, record_time)
                        SELECT id, user_id, record_type, CAST(value AS TEXT), unit, note, record_time
                        FROM health_records
                    ''')
                    
                    # 删除原表
                    cursor.execute('DROP TABLE health_records')
                    
                    # 重命名临时表
                    cursor.execute('ALTER TABLE health_records_temp RENAME TO health_records')
                    break
        except Exception as e:
            print(f"修改表结构失败: {e}")
        
        conn.commit()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medication_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                medication_name TEXT,
                dosage TEXT,
                reminder_time TEXT,
                frequency TEXT,
                is_active INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                account_type TEXT,
                account_number TEXT,
                account_name TEXT,
                is_default INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                payment_type TEXT,
                amount REAL,
                status TEXT,
                payment_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                notification_type TEXT,
                is_read INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                contact_type TEXT,
                name TEXT,
                phone_number TEXT,
                relationship TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS community_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                notification_type TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES admins(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                is_available INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (created_by) REFERENCES admins(id)
            )
        ''')
        
        # 保存用户常用的地址和电话
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_order_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                address TEXT NOT NULL,
                phone TEXT NOT NULL,
                use_count INTEGER DEFAULT 1,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 添加默认管理员账号
        cursor.execute('SELECT * FROM admins WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', ('admin', '123456'))
        
        conn.commit()
        conn.close()
    
    def add_health_record(self, record_type, value, unit, note=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO health_records (record_type, value, unit, note)
            VALUES (?, ?, ?, ?)
        ''', (record_type, value, unit, note))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_health_records(self, record_type=None, limit=10):
        conn = self.get_connection()
        cursor = conn.cursor()
        if record_type:
            cursor.execute('''
                SELECT * FROM health_records 
                WHERE record_type = ? 
                ORDER BY record_time DESC 
                LIMIT ?
            ''', (record_type, limit))
        else:
            cursor.execute('''
                SELECT * FROM health_records 
                ORDER BY record_time DESC 
                LIMIT ?
            ''', (limit,))
        records = cursor.fetchall()
        conn.close()
        return records
    
    def get_all_health_records(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM health_records 
            ORDER BY record_time DESC
        ''')
        records = cursor.fetchall()
        conn.close()
        return records
    
    def clear_health_records(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM health_records')
        conn.commit()
        conn.close()
    
    def add_medication_reminder(self, medication_name, dosage, reminder_time, frequency):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO medication_reminders (medication_name, dosage, reminder_time, frequency)
            VALUES (?, ?, ?, ?)
        ''', (medication_name, dosage, reminder_time, frequency))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_medication_reminders(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM medication_reminders WHERE is_active = 1')
        reminders = cursor.fetchall()
        conn.close()
        return reminders
    
    def add_notification(self, title, content, notification_type):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (title, content, notification_type)
            VALUES (?, ?, ?)
        ''', (title, content, notification_type))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_notifications(self, unread_only=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        if unread_only:
            cursor.execute('SELECT * FROM notifications WHERE is_read = 0 ORDER BY created_at DESC')
        else:
            cursor.execute('SELECT * FROM notifications ORDER BY created_at DESC')
        notifications = cursor.fetchall()
        conn.close()
        return notifications
    
    def mark_notification_read(self, notification_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notification_id,))
        conn.commit()
        conn.close()
    
    def add_payment_account(self, account_type, account_number, account_name, is_default=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payment_accounts (account_type, account_number, account_name, is_default)
            VALUES (?, ?, ?, ?)
        ''', (account_type, account_number, account_name, 1 if is_default else 0))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_payment_accounts(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payment_accounts')
        accounts = cursor.fetchall()
        conn.close()
        return accounts
    
    def add_payment_record(self, payment_type, amount, status="completed"):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payment_history (payment_type, amount, status)
            VALUES (?, ?, ?)
        ''', (payment_type, amount, status))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_payment_history(self, limit=10):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payment_history ORDER BY payment_time DESC LIMIT ?', (limit,))
        records = cursor.fetchall()
        conn.close()
        return records
    
    def add_emergency_contact(self, contact_type, name, phone_number, relationship):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emergency_contacts (contact_type, name, phone_number, relationship)
            VALUES (?, ?, ?, ?)
        ''', (contact_type, name, phone_number, relationship))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_emergency_contacts(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM emergency_contacts')
        contacts = cursor.fetchall()
        conn.close()
        return contacts
    
    def add_admin(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO admins (username, password)
            VALUES (?, ?)
        ''', (username, password))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def verify_admin(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE username = ? AND password = ?', (username, password))
        admin = cursor.fetchone()
        conn.close()
        return admin
    
    def add_community_notification(self, title, content, notification_type, admin_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO community_notifications (title, content, notification_type, created_by)
            VALUES (?, ?, ?, ?)
        ''', (title, content, notification_type, admin_id))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_community_notifications(self, notification_type=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if notification_type:
            cursor.execute('''
                SELECT * FROM community_notifications 
                WHERE notification_type = ? 
                ORDER BY created_at DESC
            ''', (notification_type,))
        else:
            cursor.execute('''
                SELECT * FROM community_notifications 
                ORDER BY created_at DESC
            ''')
        notifications = cursor.fetchall()
        conn.close()
        return notifications
    
    def delete_community_notification(self, notification_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM community_notifications WHERE id = ?', (notification_id,))
        conn.commit()
        conn.close()
    
    def add_menu_item(self, name, price, description, admin_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO menu_items (name, price, description, created_by)
            VALUES (?, ?, ?, ?)
        ''', (name, price, description, admin_id))
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_menu_items(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM menu_items WHERE is_available = 1 ORDER BY created_at DESC')
        items = cursor.fetchall()
        conn.close()
        return items
    
    def update_menu_item(self, item_id, name=None, price=None, description=None, is_available=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if name is not None:
            updates.append('name = ?')
            params.append(name)
        if price is not None:
            updates.append('price = ?')
            params.append(price)
        if description is not None:
            updates.append('description = ?')
            params.append(description)
        if is_available is not None:
            updates.append('is_available = ?')
            params.append(is_available)
        
        params.append(item_id)
        
        if updates:
            cursor.execute(f'''
                UPDATE menu_items 
                SET {', '.join(updates)}
                WHERE id = ?
            ''', params)
            conn.commit()
        
        conn.close()
    
    def delete_menu_item(self, item_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE menu_items SET is_available = 0 WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()
    
    def save_user_order_info(self, address, phone):
        """保存用户订单信息（地址和电话）"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 检查是否已存在相同的地址和电话
        cursor.execute('''
            SELECT id, use_count FROM user_order_info 
            WHERE address = ? AND phone = ?
        ''', (address, phone))
        existing = cursor.fetchone()
        
        if existing:
            # 更新使用次数和最后使用时间
            cursor.execute('''
                UPDATE user_order_info 
                SET use_count = use_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (existing[0],))
        else:
            # 插入新记录
            cursor.execute('''
                INSERT INTO user_order_info (address, phone)
                VALUES (?, ?)
            ''', (address, phone))
        
        conn.commit()
        conn.close()
    
    def get_user_order_info(self, limit=5):
        """获取用户常用的订单信息，按使用次数和最后使用时间排序"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT address, phone, use_count FROM user_order_info 
            ORDER BY use_count DESC, last_used DESC 
            LIMIT ?
        ''', (limit,))
        records = cursor.fetchall()
        conn.close()
        return records
