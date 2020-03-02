import os
import yaml
from configparser import ConfigParser

""" ini 类的封装"""
class ConfigHandlerIni(ConfigParser):
    def __init__(self,file,encoding="utf-8"):
        super().__init__()
        self.file=file
        self.read(file,encoding=encoding)

    """获取.ini文件内容"""
    def get_ini(self,section,option):
        value=self.get(section, option)
        return value

    """修改.ini文件内容"""
    def write_ini(self,section,option,data,mode="w"): #修改完某个值后覆盖原来的所有内容
        self[section][option] = data  #直接修改 value 是不会保存到文件的，必须open file写入
        with open(self.file, mode=mode, encoding="utf-8") as f:
            w = self.write(f)

    """ yaml 类的封装"""
class ConfigHandlerYaml():
    def __init__(self,file,encoding="utf-8"):
        self.file=file
        self.encoding=encoding

    """获取.yaml文件内容"""
    def read_yaml(self):
        with open(self.file,encoding=self.encoding) as f :
             return yaml.load(f.read(),Loader=yaml.FullLoader)

    """修改.yaml文件内容"""
    def write_yaml(self,aa,encoding="utf-8"):
        data=self.read_yaml()
        data["Excel_handler"]["sheet_login"] = aa
        with open(self.file,mode="w",encoding=encoding) as f:
            yaml.dump(data,stream=f, allow_unicode=True) # allow_unicode=True 处理中文显示


class Config(ConfigHandlerYaml):

        """项目路径"""
        root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        """测试用例路径"""
        cases_path = os.path.join(root_path,"test_cases")

        """yaml文件路径"""
        yaml_path = os.path.join(root_path, r"config\api_config.yaml")

        """测试报告路径"""
        report_path = os.path.join(root_path,"report")
        if not os.path.exists(report_path):
            os.mkdir(report_path)

        """传递yaml文件路径"""
        def __init__(self,file=yaml_path):
            super().__init__(file)

        """测试数据路径"""
        def data_path(self):
            res = self.read_yaml()
            data_path=os.path.join(self.root_path,r"data\{}".format(res["Excel_handler"]["xlsx_name"]))  #TODO:文件名称放在yaml中
            return data_path

class DevConfig(Config):

    """域名地址"""
    host = "http://120.78.128.25:8766/futureloan"


config=DevConfig()













