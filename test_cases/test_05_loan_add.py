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

"""读取"新增项目"表单中的数据"""
excel_handler = ExcelHandler(config.data_path())
data = excel_handler.sheet_readAll(config.read_yaml()["Excel_handler"]["sheet_loan_add"])  # 从yaml中读取"新增项目"表单名称

@ddt.ddt
class TestLoanAdd(unittest.TestCase):
    def setUp(self) -> None: #前置条件
        """ 连接数据库"""
        self.db = DbHandler(host=config.read_yaml()["Database"]["host"], port=config.read_yaml()["Database"]["port"],
                       user=config.read_yaml()["Database"]["user"], password=config.read_yaml()["Database"]["password"],
                       charset=config.read_yaml()["Database"]["charset"], database=config.read_yaml()["Database"]["database"])

        """新增项目和登录的用例关联（或者用例依赖）"""
        # 充值、新增项目、投资使用同一测试账号
        token = Context.token_recharge #获取登录时生成的token
        member_id = Context.memberId_recharge #获取充值ID

        """将token添加进headers的字典中"""
        headers_dict = {"X-Lemonban-Media-Type":"lemonban.v2"}
        headers_dict["Authorization"]=token
        self.headers = headers_dict
        self.member_id=member_id

        print("正在准备测试数据")

    def tearDown(self) -> None: #后置条件
        """ 关闭数据库游标和连接"""
        self.db.close()
        print("测试用例执行完毕")

    """将 *data 当中的一组测试数据赋值到 data 这个参数"""
    @ddt.data(*data)
    def test_loan_add(self,test_data):
        """
        1.访问接口，获得实际结果
        2.获得预期结果
        3.断言
        TODO:如果不加json.load,是默认获取字符串而不是JSON格式，加了json.load（）相当于脱去外套，使其是JSON格式（会报AttributeError: 'str' object has no attribute 'items'错误）
        -json.loads() -json格式字符串转化为字典
        -json.dump() -字典转化为json格式字符串
        """

        """使用正则表达式匹配excel.loan中的 #memberId_recharge# 、、#wrong_memberId_recharge# ，然后映射Context类对应属性中的值进行替换 """
        test_data["json"] = replace_label(test_data["json"])

        print("正在执行第{}条用例，测试的内容是:{}".format(test_data["case_id"], test_data["case_name"]))

        """
        #假设res()是接口函数，使用mock去模拟接口返回来的数据，为了在接口还没开发好跑通自己的测试逻辑
        res = Mock(return_value = test_data["expected_result"])
        try:
            self.assertEqual(test_data["expected_result"],res())
            test_result = "pass"  # 用例测试通过
        """

        """访问"新增项目"接口"""
        res = RequestsHandle().visit(test_data["method"],
                                     config.host+test_data["url"],
                                     json=json.loads(test_data["json"]),
                                     headers=self.headers)

        """断言时需进行异常处理"""
        try:
            """可采用for循环遍历预期结果的值，进行多个断言"""
            for k,v in json.loads(test_data["expected_result"]).items():
                if k in res:
                    self.assertEqual(v,res[k])
            test_result = "pass"  # 用例测试通过

        except AssertionError as e:
            print("断言失败，错误信息如下：{}".format(e))
            test_result = "fail"  # 用例测试失败
            logger.error(e) # 将错误信息记录到日志文件中
            raise AssertionError #手动抛出异常，不然会测试通过

        finally:
            column_actualResult=excel_handler.sheet_header(config.read_yaml()["Excel_handler"]["sheet_loan_add"]).index("actual_result") #获取"loan_add"表单标题中"actual_result"索引值
            ExcelHandler.sheet_writeCell(config.data_path(),
                                         config.read_yaml()["Excel_handler"]["sheet_loan_add"],
                                         test_data["case_id"]+1,
                                         column_actualResult+1,
                                         str(res))  # 向actual_result写值

            column_testResult=excel_handler.sheet_header(config.read_yaml()["Excel_handler"]["sheet_loan_add"]).index("test_result") #获取"loan_add"表单标题中"test_result"索引值
            ExcelHandler.sheet_writeCell(config.data_path(),
                                         config.read_yaml()["Excel_handler"]["sheet_loan_add"],
                                         test_data["case_id"]+1,
                                         column_testResult+1,
                                         test_result)  # 向test_result填写测试结果，"pass"or"fail"

if __name__ == "__main__":  # 使用python运行
    unittest.main()
