import unittest
import os
from datetime import datetime
from config.setting import config
from libs.HTMLTestRunnerNew import HTMLTestRunner

"""初始化加载器"""
testloader=unittest.TestLoader()

"""加载test_case中所有模块的测试用例 """

suite=testloader.discover(config.cases_path)

"""
测试报告(html)及运行测试用例
HTMLTestRunner，不是Unittest自带的，需要自己去安装
1、复制到项目目录下，然后导入
2、放到python的公共库中（Lib或者site-packages）
"""
ts=datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  #根据时间生成测试报告
report_path=os.path.join(config.report_path,"html_{}.html".format(ts))

with open(report_path,"wb") as f: #一定要用二进制打开
    runner=HTMLTestRunner(f,title="前程贷接口测试报告",description="前程贷接口测试报告",tester="小战")  #verbosity可切换测试报告的显示形式
    runner.run(suite)

#加载指定模块，也可模块间合并加载
# from python_test.test_case import test_1,test_2
# suite_1=testloader.loadTestsFromModule(test_1)
# suite_2=testloader.loadTestsFromModule(test_2)
# suite_total=unittest.TestSuite()
# suite_total.addTest(suite_1)
# suite_total.addTest(suite_2)

#加载指定测试类，也可类与类合并加载
# from python_test.test_case.test_1 import TestLogin
# from python_test.test_case.test_2 import TestEqual
# suite_1=testloader.loadTestsFromTestCase(TestLogin)
# suite_2=testloader.loadTestsFromTestCase(TestEqual)
# suite_total=unittest.TestSuite()
# suite_total.addTest(suite_1)
# suite_total.addTest(suite_2)


#测试报告(text)及运行测试用例
# report_path=os.path.join(dir_name,"report")
# if not os.path.exists(report_path):
#     os.mkdir(report_path)
# report_text_path=os.path.join(report_path,"report_1.txt")
#
# with open(report_text_path,"w",encoding="utf-8") as f:
#     runner=unittest.TextTestRunner(f,verbosity=2)  #verbosity可切换测试报告的显示形式
#     runner.run(suite)


