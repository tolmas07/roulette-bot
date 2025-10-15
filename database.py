import sqlite3
from config import STARTING_BALANCE

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('users.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        # Таблица пользователей
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users
            (user_id INT PRIMARY KEY NOT NULL,
            balance INT NOT NULL,
            username TEXT DEFAULT '');
        ''')
        
        # Таблица истории игр
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS game_history
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INT NOT NULL,
            username TEXT,
            bet_amount INT,
            winning_number INT,
            win_amount INT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);
        ''')
        
        # Таблица активных ставок
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS active_bets
            (user_id INT PRIMARY KEY NOT NULL,
            bet_amount INT,
            bet_type TEXT,
            bet_value TEXT);
        ''')
    
    def get_balance(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            self.conn.execute("INSERT INTO users (user_id, balance, username) VALUES (?, ?, ?)",
                            (user_id, STARTING_BALANCE, ""))
            self.conn.commit()
            return STARTING_BALANCE
    
    def update_balance(self, user_id, amount):
        self.conn.execute("UPDATE users SET balance=? WHERE user_id=?", (amount, user_id))
        self.conn.commit()
    
    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id, balance, username FROM users")
        return cursor.fetchall()
    
    def set_balance(self, user_id, new_balance):
        self.conn.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
        self.conn.commit()
    
    def update_username(self, user_id, username):
        self.conn.execute("UPDATE users SET username=? WHERE user_id=?", (username, user_id))
        self.conn.commit()
    
    # Методы для активных ставок
    def set_active_bet(self, user_id, bet_amount, bet_type, bet_value):
        self.conn.execute(
            "INSERT OR REPLACE INTO active_bets (user_id, bet_amount, bet_type, bet_value) VALUES (?, ?, ?, ?)",
            (user_id, bet_amount, bet_type, bet_value)
        )
        self.conn.commit()
    
    def get_active_bet(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT bet_amount, bet_type, bet_value FROM active_bets WHERE user_id=?", (user_id,))
        return cursor.fetchone()
    
    def clear_active_bet(self, user_id):
        self.conn.execute("DELETE FROM active_bets WHERE user_id=?", (user_id,))
        self.conn.commit()
    
    # Методы для истории игр
    def add_game_history(self, user_id, username, bet_amount, winning_number, win_amount):
        self.conn.execute(
            "INSERT INTO game_history (user_id, username, bet_amount, winning_number, win_amount) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, bet_amount, winning_number, win_amount)
        )
        self.conn.commit()
    
    def get_game_history(self, user_id, limit=10):
        cursor = self.conn.cursor()
        # Получаем последние 10 записей и переворачиваем порядок
        cursor.execute(
            "SELECT winning_number FROM game_history WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit)
        )
        results = cursor.fetchall()
        # Переворачиваем список чтобы старые были сверху, новые снизу
        return list(reversed(results))