import pymysql
from pymysql.cursors import DictCursor
from config.setting import config

"""
数据库：mysql、oracle、sqlserver、mongodb、access
操作mysql数据库：db-api、pymysql
操作步骤：
- 连接数据库 conn = pymysql.connect()
- 获取游标 cursor = conn.cursor()
- 执行sql语句 cursor.execute()
- 获取查询结果 cursor.fetchone() or cursor.fetchall()
- 关闭游标、关闭连接 cursor.close()、conn.close()

"""
#封装数据库操作
class DbHandler():
    def __init__(self,host=None,port=None,
                user=None,password=None,
                charset=None,database=None,**kwargs):
        """初始化"""
        self.conn = pymysql.connect(host=host,port=port,  #主机 端口
                                    user=user,password=password, #用户名 密码
                                    charset=charset,database=database, #编码格式 数据库名
                                    cursorclass=DictCursor)  #DictCursor将从数据库获取的记录用字典存储，默认是元组
        """获取游标"""
        self.cursor=self.conn.cursor()

    def query(self,sql,args=None,one=True):
        """args 参数用来传递参数，填%s的坑 , 例如：select * from member limit 1 where mobile_phone = %s;"""

        """查询语句"""
        self.cursor.execute(sql,args)

        #TODO：提交事务，同步数据
        self.conn.commit()

        """获取结果"""
        if one:
            res = self.cursor.fetchone()
        else:
            res = self.cursor.fetchall()
        return res

    def close(self):
        self.cursor.close()  #关闭游标
        self.conn.close() #关闭连接

if __name__=="__main__":
    db_data=config.read_yaml()  #从yaml文件中读取相关配置参数
    db=DbHandler(host=db_data["Database"]["host"],port=db_data["Database"]["port"],
                 user=db_data["Database"]["user"],password=db_data["Database"]["password"],
                 charset=db_data["Database"]["charset"],database=db_data["Database"]["database"])
    print(db.query("select * from member where mobile_phone=%s and id=%s;",args=["15917169660",900476]))