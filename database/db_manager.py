import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """データベースにテーブルを作成する"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                table_number INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_menu_item(self, name, price):
        """メニュー項目を追加する"""
        self.cursor.execute('''
            INSERT INTO menu (name, price) VALUES (?, ?)
        ''', (name, price))
        self.conn.commit()

    def add_order(self, table_number, items):
        """注文をデータベースに保存する"""
        for item in items:
            self.cursor.execute('''
                INSERT INTO orders (table_number, item_name) VALUES (?, ?)
            ''', (table_number, item))
        self.conn.commit()

    def get_orders_by_table(self, table_number):
        """指定された席番号の注文を取得する"""
        self.cursor.execute("SELECT item_name FROM orders WHERE table_number = ?", (table_number,))
        return self.cursor.fetchall()
        
    def is_table_occupied(self, table_number):
        """指定された席番号に注文があるか確認する"""
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE table_number = ?", (table_number,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def clear_table_orders(self, table_number):
        """指定された席番号の注文をすべて削除する（会計処理）"""
        self.cursor.execute("DELETE FROM orders WHERE table_number = ?", (table_number,))
        self.conn.commit()

    def clear_menu(self):
        """メニューテーブルをクリアする"""
        self.cursor.execute("DELETE FROM menu")
        self.conn.commit()

    def search_menu(self, keyword):
        """メニュー名で部分一致検索を行う関数"""
        self.cursor.execute("SELECT name, price FROM menu WHERE name LIKE ?", ('%' + keyword + '%',))
        return self.cursor.fetchall()

    def close(self):
        """データベース接続を閉じる"""
        self.conn.close()