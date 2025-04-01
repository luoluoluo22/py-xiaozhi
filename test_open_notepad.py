import asyncio
import logging
from src.utils.system_commands import SystemCommands

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_open_notepad():
    """测试打开记事本的功能"""
    print("=== 开始测试打开记事本 ===")
    
    # 1. 直接使用 open_application
    print("\n1. 测试 open_application 方法:")
    result = SystemCommands.open_application("记事本")
    print(f"直接打开结果: {result}")
    
    # 2. 使用 handle_iot_command
    print("\n2. 测试 handle_iot_command 方法:")
    iot_command = {
        "name": "系统命令",
        "method": "Query",
        "parameters": {
            "query": "打开记事本"
        }
    }
    result = SystemCommands.handle_iot_command(iot_command)
    print(f"IoT命令打开结果: {result}")
    
    # 3. 测试不同的应用名称变体
    print("\n3. 测试不同的应用名称:")
    variants = ["notepad", "notepad.exe", "记事本.exe", "记事本"]
    for name in variants:
        print(f"\n测试打开 {name}:")
        result = SystemCommands.open_application(name)
        print(f"结果: {result}")

    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_open_notepad()) 