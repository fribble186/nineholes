from gevent import monkey;monkey.patch_all()
import gevent
import pymysql


class BaseMysqlFetcher:
    def __init__(self, host, port, user, pwd, db):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db
        self.client = None
        self.cursor = None


class AsMysqlFetcher(BaseMysqlFetcher):

    def connect(self):
        if not self.client:
            self.client = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.pwd,
                db=self.db,
                port=self.port,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor,
            )

        if not self.cursor:
            self.cursor = self.client.cursor()

    def get_cursor(self):
        if not self.cursor:
            self.cursor = self.client.cursor()

    def close(self):
        self.cursor.close()

    def execute(self, sql):
        self.client.ping(reconnect=True)
        results = self.cursor.execute(sql)
        self.client.commit()
        return results

    def fetchall(self, sqls):
        try:
            tasks = [gevent.spawn(self.execute, (sql)) for sql in sqls]
            gevent.joinall(tasks, timeout=10)
            return tasks
        except Exception as e:
            print(e)
