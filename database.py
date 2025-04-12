import sqlite3

def init_db():
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            max_stamina INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def set_max_stamina(user_id, max_stamina):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('REPLACE INTO users (user_id, max_stamina) VALUES (?, ?)', (user_id, max_stamina))
    conn.commit()
    conn.close()

def get_max_stamina(user_id):
    conn = sqlite3.connect('user_data.db')
    c = conn.cursor()
    c.execute('SELECT max_stamina FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

init_db()
