# @Time : 2020.7.17
# @Author : LeeWJ
# @Function  :  配置文件读取模块
# @Version  : 2.1

from common import logger
from common.yml import Yml
#from common.txt import Txt

# 全局变量，用来存储配置
configdict = {}

def get_config(path):
    """
    读取配置文件,配置文件格式：#为注释，配置格式见yaml格式
    :param path:配置文件路径
    :return:返回配置文件dict
    """
    global configdict
    configdict.clear()
    configdict = Yml(path).read_yml()
    return configdict