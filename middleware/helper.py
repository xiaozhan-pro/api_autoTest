import re
import random

from jsonpath import jsonpath
from common.Request_handler import RequestsHandle
from common.db_handler import DbHandler
from config.setting import config

def generate_mobile():
    """随机生成一个手机号码 1+[3,5,7,8,9]+9位数字"""
    phone= "1" + random.choice(["3","5","7","8","9"])
    for i in range(9):
        num=random.randint(0,9)  # 0和9都取
        phone += str(num)
    return  phone

def login():
    """登录获取token，访问充值接口"""
    res_recharge=RequestsHandle().visit("post",
                               config.host + "/member/login",
                               json=config.read_yaml()["User_RechargeTest"],
                               headers={"X-Lemonban-Media-Type":"lemonban.v2"})

    """登录获取token，访问提现接口"""
    res_withdraw=RequestsHandle().visit("post",
                               config.host + "/member/login",
                               json=config.read_yaml()["User_WithdrawTest"],
                               headers={"X-Lemonban-Media-Type":"lemonban.v2"})


    return {"res_recharge":res_recharge,"res_withdraw":res_withdraw}

def save_rechargeToken():
    """
    jsonpath ==> 专门用来解析json的路径工具
    - $ 根节点
    - . 子节点
    - .. 子孙节点

    导入步骤：
    1、安装jsonpath库
    2、引入
    """
    res = login()["res_recharge"]
    token = jsonpath(res,"$...token")[0]
    token_type = jsonpath(res,"$...token_type")[0]
    member_id = jsonpath(res,"$..id")[0]

    """拼接token"""
    token=" ".join([token_type,token])

    return {"token":token,"member_id":member_id}

def save_withdrawToken():

    res = login()["res_withdraw"]
    token = jsonpath(res,"$...token")[0]
    token_type = jsonpath(res,"$...token_type")[0]
    member_id = jsonpath(res,"$..id")[0]

    """拼接token"""
    token=" ".join([token_type,token])

    return {"token":token,"member_id":member_id}

# 将替换封装成函数
def replace_label(target):
    """while 循环"""
    re_pattern = r"#(.*?)#"
    while re.findall(re_pattern, target):
        """如果能匹配"""
        key = re.search(re_pattern,target).group(1) #key是target匹配到的字符串，需要和类属性的名称一一映射
        target = re.sub(re_pattern, str(getattr(Context(),key)), target, 1)  #把Context类中属性的值替换到target中去,getattr括号内的类需要实例化（加括号）
    return target

class Context():
    """存储临时数据"""
    token_recharge = save_rechargeToken()["token"]
    memberId_recharge = save_rechargeToken()["member_id"]
    wrong_memberId_recharge = save_rechargeToken()["member_id"] + 1 #错误的member_id号

    token_withdraw = save_withdrawToken()["token"]
    memberId_withdraw = save_withdrawToken()["member_id"]
    wrong_memberId_withdraw = save_rechargeToken()["member_id"] + 1  # 错误的member_id号

    """
    获取处于竞标状态且未满标的项目id
    装饰了 @property 就可以把 loan_id 直接当成类属性使用  
    """
    @property
    def loan_id(self):
        self.db = DbHandler(host=config.read_yaml()["Database"]["host"], port=config.read_yaml()["Database"]["port"],
                       user=config.read_yaml()["Database"]["user"], password=config.read_yaml()["Database"]["password"],
                       charset=config.read_yaml()["Database"]["charset"], database=config.read_yaml()["Database"]["database"])

        sql = self.db.query("select * from loan where status=2 and full_time is null limit 100;")
        loan_id = sql["id"]
        self.db.close()
        return loan_id

if __name__ == "__main__":
    mystr = '{"member_id":"#memberId_recharge#","loan_id":"#loan_id#"}'
    print(replace_label(mystr))

