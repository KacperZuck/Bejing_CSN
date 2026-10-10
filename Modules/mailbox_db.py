import sqlite3
import os
from Modules.logger import logger


class MailboxDB:
    """Manages the local SQLite database for downloaded messages."""

    def __init__(self, db_name="mailbox.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, db_name)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS messages
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                msg_number
                                INTEGER,
                                sender
                                TEXT,
                                subject
                                TEXT,
                                date
                                TEXT,
                                body
                                TEXT
                            )
                            ''')
        self.conn.commit()
        logger.info("Initialized local SQLite database.")

    def save_message(self, msg_number, sender, subject, date, body):
        self.cursor.execute('''
                            INSERT INTO messages (msg_number, sender, subject, date, body)
                            VALUES (?, ?, ?, ?, ?)
                            ''', (msg_number, sender, subject, date, body))
        self.conn.commit()
        logger.info(f"Message saved locally: {subject}")

    def get_all_messages(self):
        self.cursor.execute('SELECT * FROM messages')
        return self.cursor.fetchall()