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
    country varchar(100),
    area VARCHAR(100),
    city VARCHAR(100),
    street VARCHAR(100),
    house VARCHAR(50),
    full_address VARCHAR(200),
    short_address VARCHAR(100),
    lat FLOAT(12, 8),
    lon FLOAT(12, 8),
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);''')

conn.execute('''CREATE TABLE IF NOT EXISTS csrf_tokens (
    id INTEGER PRIMARY KEY,
    token VARCHAR(250),
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);''')


conn.execute('''CREATE TABLE IF NOT EXISTS session_fast_mode (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER REFERENCES users(chat_id) ON DELETE CASCADE,
    address_1 varchar(100),
    address_2 varchar(100),
    address_3 varchar(100),
    address_4 varchar(100),
    result varchar(50),
    offer_used VARCHAR(250) REFERENCES offers_taxi(offer) ON DELETE CASCADE,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed TIMESTAMP
);''')


conn.execute('''CREATE TABLE IF NOT EXISTS offers_taxi (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER REFERENCES users(chat_id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES session_fast_mode(id) ON DELETE CASCADE,
    offer VARCHAR(250),
    price INTEGER,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);''')

conn.execute('''CREATE TABLE IF NOT EXISTS session_slow_mode (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER REFERENCES users(chat_id) ON DELETE CASCADE,
    enable INTEGER DEFAULT 1,
    time_start VARCHAR(10),
    time_end VARCHAR(10),
    address_1 varchar(100),
    address_2 varchar(100),
    address_3 varchar(100),
    address_4 varchar(100),
    result varchar(50),
    offer_used VARCHAR(250) REFERENCES offers_taxi(offer) ON DELETE CASCADE,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed TIMESTAMP
);''')

conn.execute('''CREATE TABLE IF NOT EXISTS offers_taxi_slow_mode (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER REFERENCES users(chat_id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES session_fast_mode(id) ON DELETE CASCADE,
    offer VARCHAR(250),
    price INTEGER,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);''')


conn.commit()
conn.close()




