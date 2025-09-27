import pymysql
import sqlite3

class MysqlHelper(object):
    def __init__(self, host, user, password, port, database):
        self.host = host
        self.user = user
        self.password = password
        self.port = int(port)
        self.database = database
        self.connection = None

    def connect(self):
        self.connection = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          port=self.port, database=self.database)

    def select(self, sql):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
            return result
        except Exception as e:
            print(u'查询错误...', e)
        finally:
            self.connection.close()

    def operate(self, sql):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                self.connection.commit()
        except Exception as e:
            print(u'修改失败，数据库回滚...', e)
            self.connection.rollback()
        finally:
            self.connection.close()


class SqliteHelper(object):

    def __init__(self,database=''):
        self.database = database
        self.connection = None

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def connect(self):
        self.connection = sqlite3.connect(self.database)
        self.connection.row_factory = self.dict_factory

    def select(self, sql):
        try:
            self.connect()
            cursor = self.connection.cursor().execute(sql)
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(u'查询错误...', e)
        finally:
            self.connection.close()

    def operate(self, sql):
        try:
            self.connect()
            self.connection.cursor().execute(sql)
            self.connection.commit()
        except Exception as e:
            print(u'修改失败，数据库回滚...', e)
            self.connection.rollback()
        finally:
            self.connection.close()