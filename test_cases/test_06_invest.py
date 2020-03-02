import unittest
import json

from mock import Mock
from decimal import Decimal
from common.db_handler import DbHandler
from libs import ddt
from common.Excel_handler import ExcelHandler
from common.Request_handler import RequestsHandle
from common.Logger_handler import LoggerHandler
from config.setting import config  #小技巧：直接导入实例对象，避免路径被修改导致报错
from middleware.helper import Context,replace_label

"""初始化日志处理器"""
logger=LoggerHandler()

"""读取"投资"表单中的数据"""
excel_handler = ExcelHandler(config.data_path())
data = excel_handler.sheet_readAll(config.read_yaml()["Excel_handler"]["sheet_invest"])  # 从yaml中读取"投资"表单名称

@ddt.ddt
class TestInvest(unittest.TestCase):
    def setUp(self) -> None: #前置条件
        """ 连接数据库"""
        self.db = DbHandler(host=config.read_yaml()["Database"]["host"], port=config.read_yaml()["Database"]["port"],
                       user=config.read_yaml()["Database"]["user"], password=config.read_yaml()["Database"]["password"],
                       charset=config.read_yaml()["Database"]["charset"], database=config.read_yaml()["Database"]["database"])

        """投资和登录的用例关联（或者用例依赖）,而且充值、新增项目、投资使用同一测试账号"""

        """获取登录时生成的token"""
        token = Context.token_recharge

        """将投资账号的token添加进headers的字典中"""
        headers_dict = {"X-Lemonban-Media-Type":"lemonban.v2"}
        headers_dict["Authorization"]=token
        self.headers = headers_dict

        print("正在准备测试数据")

    def tearDown(self) -> None: #后置条件
        """ 关闭数据库游标和连接"""
        self.db.close()
        print("测试用例执行完毕")

    """将 *data 当中的一组测试数据赋值到 data 这个参数"""
    @ddt.data(*data)
    def test_invest(self,test_data):
        """
        1.访问接口，获得实际结果
        2.获得预期结果
        3.断言
        TODO:如果不加json.load,是默认获取字符串而不是JSON格式，加了json.load（）相当于脱去外套，使其是JSON格式（会报AttributeError: 'str' object has no attribute 'items'错误）
        -json.loads() -json格式字符串转化为字典
        -json.dump() -字典转化为json格式字符串
        """

        """使用正则表达式匹配excel.invest中的 #memberId_recharge# 、#loan_id# 、#wrong_memberId_recharge# ，然后映射Context类对应属性中的值进行替换 """
        test_data["json"] = replace_label(test_data["json"])

        """
        替换excel.invest中的 *above_balance*
        
        测试用例：投资金额大于用户余额
        用例会出现两种情况：
        - 投资金额大于用户余额，同时大于项目可投金额，会报错 "该标可投金额不足,可投金额：xxxx"，测试OK
        - 投资金额大于用户余额，但是小于等于项目可投金额，仍然可以投资成功，资产负债，测试OK
        """

        """查询数据库，查询登录后的余额"""
        user = self.db.query("select * from member where id=%s;",args=[Context.memberId_recharge])
        before_money = user["leave_amount"]

        if "*above_balance*" in test_data["json"]:

            """如果登录后的余额为负数，转化为正数"""
            if before_money < 0 :
                before_money = before_money *(-1)

            """将登录后的余额进行取整、转化为能被100整除（目的是使投资金额必须为能被100整除的整数），再加100使其投资金额大于账户余额"""
            test_data["json"] = test_data["json"].replace("*above_balance*", str(int(before_money)-(int(before_money) % 100) + 100))  # 注意将ID转化为字符串

        print("正在执行第{}条用例，测试的内容是:{}".format(test_data["case_id"], test_data["case_name"]))

        """
        #假设res()是接口函数，使用mock去模拟接口返回来的数据，为了在接口还没开发好跑通自己的测试逻辑
        res = Mock(return_value = test_data["expected_result"])
        try:
            self.assertEqual(test_data["expected_result"],res())
            test_result = "pass"  # 用例测试通过
        """
        
        """访问"投资"接口"""
        res = RequestsHandle().visit(test_data["method"],
                                         config.host+test_data["url"],
                                         json=json.loads(test_data["json"]),
                                         headers=self.headers)

        """断言时需进行异常处理"""
        try:
            """可采用for循环遍历预期结果的值，进行多个断言"""
            for k, v in json.loads(test_data["expected_result"]).items():
                if k in res:
                    self.assertEqual(v, res[k])

            # """查看数据库结果，登录后的余额 - 投资金额 = 投资后的余额"""
            if res["code"]== 0:
                money = json.loads(test_data["json"])["amount"]

                """查询数据库，查询投资后的余额"""
                after_user = self.db.query("select * from member where id=%s;", args=[Context.memberId_recharge])
                after_money = after_user["leave_amount"]

                try:
                    """断言 登录后的余额 - 投资金额 是否等于 投资后的余额"""
                    self.assertEqual(Decimal(str(before_money)) - Decimal(str(money)), Decimal(str(after_money)))
                    """用例测试通过"""
                    test_result = "pass"

                except AssertionError as e:
                    print("断言失败，错误信息如下：{}".format(e))
                    test_result = "fail"  # 用例测试失败
                    logger.error(e)  # 将错误信息记录到日志文件中
                    raise AssertionError  # 手动抛出异常，不然会测试通过

            if res["code"] != 0:
                """用例测试通过"""
                test_result = "pass"

        except AssertionError as e:
            print("断言失败，错误信息如下：{}".format(e))
            test_result = "fail"  # 用例测试失败
            logger.error(e) # 将错误信息记录到日志文件中
            raise AssertionError #手动抛出异常，不然会测试通过

        finally:
            column_actualResult=excel_handler.sheet_header(config.read_yaml()["Excel_handler"]["sheet_invest"]).index("actual_result") #获取"invest"表单标题中"actual_result"索引值
            ExcelHandler.sheet_writeCell(config.data_path(),
                                         config.read_yaml()["Excel_handler"]["sheet_invest"],
                                         test_data["case_id"]+1,
                                         column_actualResult+1,
                                         str(res))  # 向actual_result写值

            column_testResult=excel_handler.sheet_header(config.read_yaml()["Excel_handler"]["sheet_invest"]).index("test_result") #获取"invest"表单标题中"test_result"索引值
            ExcelHandler.sheet_writeCell(config.data_path(),
                                         config.read_yaml()["Excel_handler"]["sheet_invest"],
                                         test_data["case_id"]+1,
                                         column_testResult+1,
                                         test_result)  # 向test_result填写测试结果，"pass"or"fail"

if __name__ == "__main__":  # 使用python运行
    unittest.main()

