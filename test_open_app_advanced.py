import asyncio
import logging
import sys
import time
from src.utils.system_commands import SystemCommands

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("TestOpenAppAdvanced")

def test_open_app_basic(app_name):
    """测试基本的应用程序打开功能"""
    logger.info(f"===== 开始测试打开应用: {app_name} =====")
    
    # 直接使用SystemCommands.open_application
    success = SystemCommands.open_application(app_name)
    
    logger.info(f"打开结果: {'成功' if success else '失败'}")
    return success

def test_get_program_path(app_name):
    """测试程序路径查找功能"""
    logger.info(f"===== 测试查找程序路径: {app_name} =====")
    
    # 使用_get_program_path查找路径
    path = SystemCommands._get_program_path(app_name)
    
    if path:
        logger.info(f"找到路径: {path}")
    else:
        logger.info(f"未找到路径")
    
    return path

def run_tests():
    """运行所有测试"""
    # 测试系统应用
    test_open_app_basic("记事本")
    time.sleep(2)  # 等待程序打开
    SystemCommands.close_application("记事本")
    time.sleep(1)
    
    # 测试中文名和英文名
    test_get_program_path("微信")
    test_get_program_path("WeChat.exe")
    test_get_program_path("wechat")
    
    # 测试在开始菜单中查找程序
    test_get_program_path("微信")
    
    # 测试特殊路径查找
    test_get_program_path("QQ")
    test_get_program_path("chrome")
    
    # 测试打开常用应用（根据系统实际安装情况可能成功或失败）
    print("\n是否要测试打开微信? (y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        success = test_open_app_basic("微信")
        if success:
            print("测试成功! 5秒后将关闭微信...")
            time.sleep(5)
            SystemCommands.close_application("微信")
    
    print("\n是否要测试打开QQ? (y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        success = test_open_app_basic("QQ")
        if success:
            print("测试成功! 5秒后将关闭QQ...")
            time.sleep(5)
            SystemCommands.close_application("QQ")
    
    # 测试不存在的应用
    test_open_app_basic("不存在的应用XYZ")
    
    logger.info("===== 所有测试完成 =====")

if __name__ == "__main__":
    run_tests() 