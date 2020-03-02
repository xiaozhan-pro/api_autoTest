"""
log日志
日志：记录信息，便于我们查看问题和定位问题
使用前需导入标准库 logging
logging.NOTSET 级别号：0 等于没写
logging.debug() 级别号：10 调试信息
logging.info() 级别号：20  主体功能信息
logging.warning() 级别号：30 警告
logging.error() 级别号：40  错误
logging.critical() 级别号：50 极其严重的BUG
**********
-1. 日志的收集器 logger:日记本
-2. 日志收集器级别 level
-3. 日志处理器准备 handler 不同记号的笔
-4. 日志处理器级别设置
-5. 添加处理器 logger.addHandler(handler)
-6. 设置日志格式 format
-7. 设置日志格式至处理器 handler.setFormatter()

设置级别：
当设成debug的时候，只有高于或等于该级别才会打印

处理器主要格式说明：
-%(asctime)s 时间
-%(funcName)s 封装的函数名
-%(filename)s 文件名
-%(levelno)s  级别号
-%(lineno)d  行号
-%(levelname)s  级别名
-%(name)s 收集器名
-%(message)s 主要信息


"""
import logging
from config.setting import config

class LoggerHandler(logging.Logger): #TODO:此处用继承的方法可以解决输出行号不对的问题
    """ 读取配置表中的常量'log_name'和'filename' """
    def __init__(self,log_name=config.read_yaml()["Logger_handler"]["log_name"],filename=config.read_yaml()["Logger_handler"]["filename"],HandlerLevel="DEBUG",StreamHandler="DEBUG"):
        """在父类创建实例，并且初始化logger收集器"""
        super().__init__(log_name)

        """设置级别"""
        self.setLevel("DEBUG")

        """设置handler格式"""
        fmt=logging.Formatter("%(filename)s-%(lineno)d-%(levelname)s-%(name)s-%(message)s-%(asctime)s")

        """初始化处理器/设置处理器级别/设置处理器格式"""
        if log_name:
            handler=logging.FileHandler(filename) #file文件输出
            handler.setLevel(HandlerLevel)
            handler.setFormatter(fmt)
            self.addHandler(handler)
        console_handler=logging.StreamHandler() #控制台输出
        console_handler.setLevel(StreamHandler)
        console_handler.setFormatter(fmt)
        self.addHandler(console_handler)
        """"""












