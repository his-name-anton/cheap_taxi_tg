import sqlite3

DB_COLUMNS = {
    'users': ['chat_id', 'first_name', 'last_name', 'user_name'],
    'user_settings': ['chat_id', 'setting_name', 'value'],
    'user_addresses': ['chat_id',
                       'region',
                       'city',
                       'street',
                       'house',
                       'full_address',
                       'timezone',
                       'geo_lat',
                       'geo_lon',
                       'postal_code']
}


class DataBase:
    def __init__(self):
        self.connection = sqlite3.connect('/Users/antonlarin/python_projects/cheap_taxi_server/data_base/cheap_taxi_db.db')
        self.cursor = self.connection.cursor()

    def insert_row(self, table: str, values: tuple) -> str:
        columns = ', '.join(DB_COLUMNS.get(table))
        sql = "INSERT INTO " + table + " (" + columns + ")" + " VALUES (" + ','.join(
            ['?' for _ in range(len(values))]) + ")"
        with self.connection:
            self.cursor.execute(sql, values)

    def update_value(self, sql):
        with self.connection:
            self.cursor.execute(sql)

    def get_user(self, chat_id: int) -> int | None:
        with self.connection:
            self.cursor.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
            row = self.cursor.fetchall()
            return row[0][0] if row else None

    def get_user_value(self, chat_id: int, value) -> int | None:
        with self.connection:
            self.cursor.execute(f"SELECT {value} FROM users WHERE chat_id = ?", (chat_id,))
            row = self.cursor.fetchall()
            return row[0][0] if row else None

    def save_address(self, chat_id, add_data):
        region = add_data.get('region')
        city = add_data.get('city')
        street = add_data.get('street')
        house = add_data.get('house')
        full_address = add_data.get('full_address')
        timezone = add_data.get('timezone')
        geo_lat = add_data.get('geo_lat')
        geo_lon = add_data.get('geo_lon')
        postal_code = add_data.get('postal_code')
        with self.connection:
            self.cursor.execute(f"""
                SELECT 1
                FROM user_addresses
                WHERE chat_id = ?
                AND full_address = ?
            """, (chat_id, full_address))
            result = self.cursor.fetchall()
        if len(result) == 0:
            self.insert_row('user_addresses', (
                chat_id,
                region,
                city,
                street,
                house,
                full_address,
                timezone,
                geo_lat,
                geo_lon,
                postal_code
            ))


db = DataBase()
