from pymysql import connect
from config import *


class DB(object):
    """数据库操作管理类"""

    def __init__(self):
        # 连接到数据库
        self.conn = connect(host=DB_HOST,
                            port=DB_PORT,
                            database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS
                            )

        # 获取游标
        self.cursor = self.conn.cursor()

    def close(self):
        """释放数据库资源"""
        self.cursor.close()
        self.conn.close()

    def get_one(self, sql):
        """使用sql语句查询用户信息"""
        # 执行sql语句
        self.cursor.execute(sql)

        # 获取查询结果
        query_result = self.cursor.fetchone()

        # 判断结果
        if not query_result:
            return None

        # 获取字段名称列表
        fileds = [filed[0] for filed in self.cursor.description]

        # 使用字段和数据合成字典，返回使用
        return_data = {}
        for filed, value in zip(fileds, query_result):
            return_data[filed] = value

        return return_data

    def search_one(self, sql):
        """检查是否存在某用户"""
        # 执行sql语句
        self.cursor.execute(sql)

        # 获取查询结果
        query_result = self.cursor.fetchone()

        # 判断结果
        if query_result:
            return True

        return False

    def insert_user(self, sql):
        """插入用户信息"""
        # 执行sql语句
        self.cursor.execute(sql)
        self.conn.commit()

    def count_user(self):
        """返回用户数量"""
        self.cursor.execute("select count(*) from users")
        return self.cursor.fetchone()[0]


if __name__ == '__main__':
    db = DB()
    username = 'user6'
    password = '111111'
    nickname = 'panda6'
    user_id = 5
    print(db.count_user())
    db.close()