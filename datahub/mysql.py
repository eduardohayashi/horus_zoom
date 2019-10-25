
import json
import MySQLdb
from pythontools.verbose import *
import settings

class Mysql(object):

    def __init__(self):
        verbose('INIT MYSQL', {'host':settings.mysql_host,
        'port':settings.mysql_port, 'db':settings.mysql_database}, level=2)
        pass


    def database(self):
        db = MySQLdb.connect(
            host = settings.mysql_host,
            port = settings.mysql_port,
            user = settings.mysql_user,
            passwd = settings.mysql_password,
            db = settings.mysql_database,
            connect_timeout=60
        )

        return db


    def get_stores(self):

        conn = self.database()
        cursor = conn.cursor()
        sql = 'select slug from mvp_b2w_store where is_active=1'
        verbose(sql, level=3)
        res = cursor.execute(sql)

        result = []
        for row in cursor.fetchall():
            result.append(row[0])

        return result


    def insert_mlb(self, MLB, price, sold_quantity, available_quantity, store):
        conn = self.database()
        cursor = conn.cursor()
        sql = f'''INSERT INTO mvp_ml_prices (MLB, price, sold_quantity,
            available_quantity, store, datetime) VALUES ('{MLB}', '{price}',
            '{sold_quantity}', '{available_quantity}', '{store}', NOW())
            ON DUPLICATE KEY UPDATE price='{price}',
            sold_quantity='{sold_quantity}',
            available_quantity='{available_quantity}',
            store='{store}', datetime=NOW();'''
        verbose(sql, level=3)
        cursor.execute(sql)
        cursor.close()
        conn.commit()
        # conn.close()
