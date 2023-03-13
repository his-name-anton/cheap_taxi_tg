import math
import sqlite3
from datetime import datetime

DB_COLUMNS = {
    'users': ['chat_id', 'first_name', 'last_name', 'user_name'],
    'user_settings': ['chat_id', 'setting_name', 'value'],
    'user_addresses': ['chat_id',
                       'country',
                       'area',
                       'city',
                       'street',
                       'house',
                       'full_address',
                       'short_address',
                       'lat',
                       'lon'],
    'csrf_tokens': ['token'],
    'session_fast_mode': ['chat_id', 'address_1', 'address_2', 'address_3', 'address_4'],
    'session_slow_mode': ['chat_id', 'time_start', 'time_end', 'address_1', 'address_2', 'address_3', 'address_4'],
    'offers_taxi': ['chat_id', 'session_id', 'offer', 'price'],
    'offers_taxi_slow_mode': ['chat_id', 'session_id', 'offer', 'price']
}


class DataBase:
    def __init__(self):
        self.connection = sqlite3.connect('data_base/cheap_taxi_db.db')
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

    def get_setting_value(self, chat_id, setting_name):
        with self.connection:
            self.cursor.execute(f"""SELECT value from user_settings 
                                    where chat_id = {chat_id} 
                                    and setting_name = '{setting_name}'
                                    ORDER BY id DESC
                                    LIMIT 1""")
            row = self.cursor.fetchall()
            return row[0][0] if row else None

    def save_address(self, chat_id, add_data):
        country = add_data.get('country')
        area = add_data.get('area')
        city = add_data.get('city')
        street = add_data.get('street')
        house = add_data.get('house')
        full_address = add_data.get('full_text')
        short_address = add_data.get('short_text')
        lat = add_data.get('lat')
        lon = add_data.get('lon')
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
                country,
                area,
                city,
                street,
                house,
                full_address,
                short_address,
                lat,
                lon,
            ))

    def get_actual_token(self):
        with self.connection:
            self.cursor.execute(f"SELECT token FROM csrf_tokens order by id desc limit 1")
            row = self.cursor.fetchall()
            return row[0][0] if row else None

    def get_last_session_id(self, chat_id, table='session_fast_mode'):
        with self.connection:
            self.cursor.execute(f"""SELECT max(id) from {table} 
                                    WHERE chat_id = {chat_id} 
                                    """)
            row = self.cursor.fetchall()
            return row[0][0] if row else None

    def get_price_history(self, chat_id, session_id):
        with self.connection:
            utc = self.get_setting_value(chat_id, 'time_zone')
            self.cursor.execute(f"""
                        SELECT price,
                               datetime(ot.created, '+' || {utc} || ' hours') AS created
                        FROM offers_taxi ot
                        WHERE session_id = {session_id}
                        ORDER BY ot.id DESC LIMIT 10;
            """)
            rows = self.cursor.fetchall()
            price_list, time_list = [], []
            for row in rows:
                price_list.append(row[0])
                date_time_obj = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
                hour_minute = date_time_obj.strftime('%H:%M')
                time_list.append(hour_minute)
            return price_list[::-1], time_list[::-1]

    def get_best_price(self, session_id):
        with self.connection:
            self.cursor.execute(f"""
                    SELECT price, 
                            offer, 
                            strftime('%s', 'now') - strftime('%s', created) AS time_diff
                    FROM offers_taxi
                    WHERE id = (
                            SELECT id
                            FROM offers_taxi
                            WHERE session_id = {session_id}
                                AND created > datetime('now', '-9 minutes')
                                ORDER BY price ASC, created desc
                                LIMIT 1
                    );
            """)
            rows = self.cursor.fetchall()
            will_active = math.ceil(
                (10 * 60 - rows[0][2]) / 60)
            return rows[0][0], rows[0][1], will_active

    def set_result_session_fast_mode(self, session_id, result, best_offer=None):
        with self.connection:
            self.cursor.execute(f"""
                    UPDATE session_fast_mode
                    SET result = '{result}',
                        offer_used = '{best_offer}',
                        closed = CURRENT_TIMESTAMP
                    where id = {session_id}
            """)

    def get_recent_addresses(self, chat_id) -> dict:
        sql = f"""
            select f.lon,
        f.lat,
        f.address
        from (select t.*,
        count(t.id) OVER(partition by t.address) as cnt,
        row_number() over (partition by t.address order by t.created desc) as rank_,
        ua.lon,
        ua.lat
        from (select
            id,
            chat_id,
            address_1 as address,
            created
        from session_fast_mode

        UNION ALL

        select
            id,
            chat_id,
            address_2 as address,
            created
        from session_fast_mode

        UNION ALL

        select
            id,
            chat_id,
            address_3 as address,
            created
        from session_fast_mode

        UNION ALL

        select
            id,
            chat_id,
            address_4 as address,
            created
        from session_fast_mode) t
        join user_addresses ua on ua.short_address = t.address
        where t.chat_id = {chat_id}
        order by t.created desc
        limit 100) f
        where f.rank_ = 1
        order by f.cnt desc
        """
        with self.connection:
            self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            d = {}
            for i, row in enumerate(rows):
                d['recent_address_' + str(i)] = ([row[0], row[1]], row[2])
            return d


db = DataBase()
