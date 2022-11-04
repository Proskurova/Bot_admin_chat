import sqlite3
from time import time


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def chat_exists(self, chat_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,)).fetchall()
            return bool(len(result))

    def add_chat_channel(self, chat_id, channel_url):
        with self.connection:
            return self.connection.execute("INSERT INTO chats ('chat_id', 'channel_url') VALUES (?,?)", (chat_id, channel_url,))

    def update_channel(self, chat_id, channel_url):
        with self.connection:
            return self.cursor.execute("UPDATE chats SET channel_url = ? WHERE chat_id = ?", (channel_url, chat_id,))

    def unblock_channel(self, chat_id):
        with self.connection:
            return self.cursor.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))

    def receive_channel_url(self, chat_id):
        with self.connection:
            channel = self.cursor.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,)).fetchall()
            return channel[0][2]

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, username):
        with self.connection:
            return self.connection.execute("INSERT INTO users ('user_id', 'username') VALUES (?,?)", (user_id, username))

    def mute(self, user_id):
        with self.connection:
            user = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return int(user[3]) >= int(time())

    def add_mute(self, user_id, mute_time):
        with self.connection:
            return self.connection.execute("UPDATE users SET mute_time = ? WHERE user_id = ?",
                                           (int(time()) + mute_time, user_id,))

    def mute_del(self, user_id, mute_time):
        with self.connection:
            return self.cursor.execute("UPDATE users SET mute_time = ? WHERE user_id = ?", (mute_time, user_id,))