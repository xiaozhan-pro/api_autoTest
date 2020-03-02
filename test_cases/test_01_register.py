import unittest
import json

from mock import Mock
from libs import ddt
from common.Excel_handler import ExcelHandler
from common.Request_handler import RequestsHandle
from common.Logger_handler import LoggerHandler
from config.setting import config  #小技巧：直接导入实例对象，避免路径被修改导致报错
from common.db_handler import DbHandler
from middleware.helper import generate_mobile

"""初始化日志处理器"""
logger=LoggerHandler()

"""读取"注册"表单中的数据"""
excel_handler = ExcelHandler(config.data_path())
data = excel_handler.sheet_readAll(config.read_yaml()["Excel_handler"]["sheet_register"])  # 从yaml中读取"注册"表单名称

@ddt.ddt
class TestRegister(unittest.TestCase):
    def setUp(self) -> None: #前置条件
        """ 连接数据库"""
        self.db = DbHandler(host=config.read_yaml()["Database"]["host"], port=config.read_yaml()["Database"]["port"],
                       user=config.read_yaml()["Database"]["user"], password=config.read_yaml()["Database"]["password"],
                       charset=config.read_yaml()["Database"]["charset"], database=config.read_yaml()["Database"]["database"])
        print("正在准备测试数据")

    def tearDown(self) -> None: #后置条件
        """ 关闭数据库游标和连接"""
        self.db.close()
        print("测试用例执行完毕")

    """将 *data 当中的一组测试数据赋值到 data 这个参数"""
    @ddt.data(*data)
    def test_register(self,test_data):
        """
        1.访问接口，获得实际结果
        2.获得预期结果
        3.断言
        TODO:如果不加json.load,是默认获取字符串而不是JSON格式，加了json.load（）相当于脱去外套，使其是JSON格式（会报AttributeError: 'str' object has no attribute 'items'错误）
        -json.loads() -json格式字符串转化为字典
        -json.dump() -字典转化为json格式字符串
        """

        """对已存在的手机号码获取测试"""
        if "#exist_phone#" in test_data["json"]:
            """查询数据库，如果数据库中存在该手机号，就直接使用这个号码"""
            exist_phone = self.db.query("select * from member limit 1;") #TODO:某些相同的手机号码在数据库中存在多条，无法通过测试
            if exist_phone:
                """替换excel中的#exist_phone#"""
                test_data["json"] =test_data["json"].replace("#exist_phone#",exist_phone["mobile_phone"])
            else:
                """
                如果数据库为空，则手动注册，然后对注册好的用户进行已存在用例测试
                """
                pass

        """创建新的手机号码测试"""
        if "#new_phone#" in test_data["json"]:

            while True:
                """生成新的手机号码并且到数据库里去查询，如果存在就再生成一次，直到生成个数据库不存在的号码为止"""
                new_phone=generate_mobile()  #TODO:某些手机号码格式不正确无法通过测试
                new_mobile = self.db.query("select * from member where mobile_phone=%s;",args=[new_phone])
                if not new_mobile:
                    break

            """替换excel中的#new_phone#"""
            test_data["json"] = test_data["json"].replace("#new_phone#",new_phone)

        print("正在执行第{}条用例，测试的内容是:{}".format(test_data["case_id"], test_data["case_name"]))

        """
        #假设res()是接口函数，使用mock去模拟接口返回来的数据，为了在接口还没开发好跑通自己的测试逻辑
        res = Mock(return_value = test_data["expected_result"])
        try:
            self.assertEqual(test_data["expected_result"],res())
            test_result = "pass"  # 用例测试通过
        """

        res = RequestsHandle().visit(test_data["method"],
                                     config.host + test_data["url"],
                                     json=json.loads(test_data["json"]),
                                     headers=json.loads(test_data["headers"]))

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
            column_actualResult=excel_handler.sheet_header(config.read_yaml()["Excel_handler"]["sheet_register"]).index("actual_result") #获取"register"表单标题中"actual_result"索引值
            ExcelHandler.sheet_writeCell(config.data_path(),
                                         config.read_yaml()["Excel_handler"]["sheet_register"],
                                         test_data["case_id"]+1,
                                         column_actualResult+1,
                                         str(res))  # 向actual_result写值

            column_testResult=excel_handler.sheet_header(config.read_yaml()["Excel_handler"]["sheet_register"]).index("test_result") #获取"register"表单标题中"test_result"索引值
            ExcelHandler.sheet_writeCell(config.data_path(),
                                         config.read_yaml()["Excel_handler"]["sheet_register"],
                                         test_data["case_id"]+1,
                                         column_testResult+1,
                                         test_result)  # 向test_result填写测试结果，"pass"or"fail"

if __name__ == "__main__":  # 使用python运行
    unittest.main()
