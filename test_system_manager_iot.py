import os
import sys
import logging
import time
import json

# 添加src目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# 导入必要的类
from src.application import Application
from src.iot.thing_manager import ThingManager
from src.iot.things.system_manager import SystemManager

def test_open_application_via_iot():
    """测试通过IoT系统打开应用程序"""
    print("\n===== 测试通过IoT系统打开记事本 =====")
    
    # 初始化应用程序实例
    app = Application.get_instance()
    
    # 初始化IoT设备
    app._initialize_iot_devices()
    
    # 获取ThingManager实例
    thing_manager = ThingManager.get_instance()
    
    # 验证SystemManager已正确注册
    system_manager = None
    for thing in thing_manager.things:
        if thing.name == "SystemManager":
            system_manager = thing
            break
    
    assert system_manager is not None, "SystemManager未正确注册"
    print("SystemManager已正确注册")
    
    # 构造打开记事本的IoT命令
    command = {
        "name": "SystemManager",
        "method": "OpenApplication",
        "parameters": {
            "app_name": "记事本"
        }
    }
    
    # 输出命令
    print(f"执行IoT命令: {json.dumps(command, ensure_ascii=False)}")
    
    # 执行命令
    result = thing_manager.invoke(command)
    
    # 输出结果
    print(f"执行结果: {json.dumps(result, ensure_ascii=False)}")
    
    # 验证结果
    assert result["status"] == "success", "执行打开记事本命令失败"
    assert result["action"] == "open", "操作类型不是open"
    assert result["app_name"] == "记事本", "应用名称不匹配"
    
    # 等待一会儿
    time.sleep(2)
    
    return result

def test_close_application_via_iot():
    """测试通过IoT系统关闭应用程序"""
    print("\n===== 测试通过IoT系统关闭记事本 =====")
    
    # 获取ThingManager实例
    thing_manager = ThingManager.get_instance()
    
    # 构造关闭记事本的IoT命令
    command = {
        "name": "SystemManager",
        "method": "CloseApplication",
        "parameters": {
            "app_name": "记事本"
        }
    }
    
    # 输出命令
    print(f"执行IoT命令: {json.dumps(command, ensure_ascii=False)}")
    
    # 执行命令
    result = thing_manager.invoke(command)
    
    # 输出结果
    print(f"执行结果: {json.dumps(result, ensure_ascii=False)}")
    
    # 验证结果
    assert result["status"] == "success", "执行关闭记事本命令失败"
    assert result["action"] == "close", "操作类型不是close"
    assert result["app_name"] == "记事本", "应用名称不匹配"
    
    return result

def test_handle_iot_message():
    """测试处理IoT消息的流程"""
    print("\n===== 测试处理IoT消息流程 =====")
    
    # 初始化应用程序实例
    app = Application.get_instance()
    
    # 构造IoT消息
    message = {
        "type": "iot",
        "commands": [
            {
                "name": "SystemManager",
                "method": "OpenApplication",
                "parameters": {
                    "app_name": "计算器"
                }
            }
        ]
    }
    
    # 输出消息
    print(f"发送IoT消息: {json.dumps(message, ensure_ascii=False)}")
    
    # 处理消息
    app._handle_iot_message(message)
    
    # 等待一会儿
    print("命令已发送，等待3秒...")
    time.sleep(3)
    
    # 构造关闭IoT消息
    close_message = {
        "type": "iot",
        "commands": [
            {
                "name": "SystemManager",
                "method": "CloseApplication",
                "parameters": {
                    "app_name": "计算器"
                }
            }
        ]
    }
    
    # 输出消息
    print(f"发送IoT关闭消息: {json.dumps(close_message, ensure_ascii=False)}")
    
    # 处理消息
    app._handle_iot_message(close_message)
    
    print("测试完成")

def main():
    """主函数"""
    print("开始测试SystemManager IoT功能...")
    
    # 测试通过IoT系统打开应用程序
    open_result = test_open_application_via_iot()
    
    # 测试通过IoT系统关闭应用程序
    close_result = test_close_application_via_iot()
    
    # 暂时注释掉这一行
    # test_handle_iot_message()
    
    print("\n所有测试通过！")

if __name__ == "__main__":
    main() 