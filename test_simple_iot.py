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
from src.iot.thing_manager import ThingManager
from src.iot.things.system_manager import SystemManager

def main():
    """主函数"""
    print("开始简单IoT测试...")
    
    # 初始化ThingManager
    thing_manager = ThingManager.get_instance()
    
    # 手动添加SystemManager
    system_manager = SystemManager()
    thing_manager.add_thing(system_manager)
    
    print(f"已注册SystemManager设备")
    
    # 构造打开记事本的IoT命令
    open_command = {
        "name": "SystemManager",
        "method": "OpenApplication",
        "parameters": {
            "app_name": "记事本"
        }
    }
    
    print(f"执行打开命令: {json.dumps(open_command, ensure_ascii=False)}")
    
    # 执行命令
    open_result = thing_manager.invoke(open_command)
    
    print(f"打开结果: {json.dumps(open_result, ensure_ascii=False)}")
    
    # 等待3秒
    print("等待3秒...")
    time.sleep(3)
    
    # 构造关闭记事本的IoT命令
    close_command = {
        "name": "SystemManager",
        "method": "CloseApplication",
        "parameters": {
            "app_name": "记事本"
        }
    }
    
    print(f"执行关闭命令: {json.dumps(close_command, ensure_ascii=False)}")
    
    # 执行命令
    close_result = thing_manager.invoke(close_command)
    
    print(f"关闭结果: {json.dumps(close_result, ensure_ascii=False)}")
    
    print("测试完成")

if __name__ == "__main__":
    main() 