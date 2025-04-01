import os
import sys
import logging
import time

# 添加src目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# 导入SystemCommands类
from src.utils.system_commands import SystemCommands

def test_open_application():
    """测试打开应用程序功能"""
    
    # 测试打开记事本
    print("\n===== 测试打开记事本 =====")
    success = SystemCommands.open_application("记事本")
    assert success, "打开记事本失败"
    
    # 等待一会儿
    time.sleep(2)
    
    # 测试关闭记事本
    print("\n===== 测试关闭记事本 =====")
    success = SystemCommands.close_application("记事本")
    assert success, "关闭记事本失败"
    
    # 测试使用英文名称打开记事本
    print("\n===== 测试使用英文名称打开记事本 =====")
    success = SystemCommands.open_application("notepad")
    assert success, "打开notepad失败"
    
    # 等待一会儿
    time.sleep(2)
    
    # 测试关闭记事本
    print("\n===== 测试使用英文名称关闭记事本 =====")
    success = SystemCommands.close_application("notepad")
    assert success, "关闭notepad失败"
    
    # 测试打开微信（如果安装了的话）
    print("\n===== 测试打开微信 =====")
    success = SystemCommands.open_application("微信")
    if success:
        print("微信启动成功，等待5秒后关闭...")
        time.sleep(5)
        
        # 测试关闭微信
        print("\n===== 测试关闭微信 =====")
        success = SystemCommands.close_application("微信")
        assert success, "关闭微信失败"
    else:
        print("微信可能未安装或无法找到，跳过测试")
    
    # 测试打开计算器
    print("\n===== 测试打开计算器 =====")
    success = SystemCommands.open_application("计算器")
    assert success, "打开计算器失败"
    
    # 等待一会儿
    time.sleep(2)
    
    # 测试关闭计算器
    print("\n===== 测试关闭计算器 =====")
    success = SystemCommands.close_application("计算器")
    assert success, "关闭计算器失败"

def test_handle_iot_command():
    """测试处理IoT命令功能"""
    
    # 测试打开记事本的IoT命令
    print("\n===== 测试IoT命令打开记事本 =====")
    command = {
        "name": "系统命令",
        "method": "Query",
        "parameters": {
            "query": "打开记事本"
        }
    }
    
    result = SystemCommands.handle_iot_command(command)
    print(f"命令执行结果: {result}")
    assert result["status"] == "success", "IoT命令打开记事本失败"
    
    # 等待一会儿
    time.sleep(2)
    
    # 测试关闭记事本的IoT命令
    print("\n===== 测试IoT命令关闭记事本 =====")
    command = {
        "name": "系统命令",
        "method": "Query",
        "parameters": {
            "query": "关闭记事本"
        }
    }
    
    result = SystemCommands.handle_iot_command(command)
    print(f"命令执行结果: {result}")
    assert result["status"] == "success", "IoT命令关闭记事本失败"

def main():
    """主函数"""
    print("开始测试SystemCommands类...")
    
    # 测试打开应用程序功能
    test_open_application()
    
    # 测试处理IoT命令功能
    test_handle_iot_command()
    
    print("\n所有测试通过！")

if __name__ == "__main__":
    main() 