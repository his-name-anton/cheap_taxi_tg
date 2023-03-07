import sqlite3

conn = sqlite3.connect('cheap_taxi_db.db')

conn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER NOT NULL UNIQUE,
    phone INTEGER,
    first_name TEXT,
    last_name TEXT,
    user_name TEXT,
    city TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')


conn.execute('''CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER REFERENCES users(chat_id) ON DELETE CASCADE,
    setting_name TEXT,
    value INTEGER,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')


conn.execute('''CREATE TABLE IF NOT EXISTS user_addresses (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER REFERENCES users(chat_id) ON DELETE CASCADE,
    region VARCHAR(100),
    city VARCHAR(100),
    street VARCHAR(100),
    house VARCHAR(50),
    full_address VARCHAR(200),
    timezone VARCHAR(50),
    geo_lat VARCHAR(20),
    geo_lon VARCHAR(20),
    postal_code VARCHAR(50),
    created TIMESTAMP WITH TIME ZONE DEFAULT (strftime('%s', 'now'))
);''')


conn.commit()
conn.close()




