import os
import sys
import logging
import time
import json
import asyncio
from typing import Dict, Any

# 添加src目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# 导入必要的类
from src.utils.system_commands import SystemCommands

async def test_system_commands():
    """测试系统命令功能"""
    print("开始测试系统命令功能...")
    
    # 测试打开记事本
    print("\n===== 测试打开记事本 =====")
    open_command = {
        "name": "系统命令",
        "method": "Query",
        "parameters": {
            "query": "打开记事本"
        }
    }
    
    print(f"执行命令: {json.dumps(open_command, ensure_ascii=False)}")
    result = SystemCommands.handle_iot_command(open_command)
    print(f"命令结果: {json.dumps(result, ensure_ascii=False)}")
    
    # 等待3秒
    print("等待3秒...")
    await asyncio.sleep(3)
    
    # 测试打开计算器
    print("\n===== 测试打开计算器 =====")
    open_calc_command = {
        "name": "系统命令",
        "method": "Query",
        "parameters": {
            "query": "打开计算器"
        }
    }
    
    print(f"执行命令: {json.dumps(open_calc_command, ensure_ascii=False)}")
    result = SystemCommands.handle_iot_command(open_calc_command)
    print(f"命令结果: {json.dumps(result, ensure_ascii=False)}")
    
    # 等待3秒
    print("等待3秒...")
    await asyncio.sleep(3)
    
    # 测试批量操作
    print("\n===== 测试批量命令 =====")
    batch_commands = [
        {
            "name": "系统命令",
            "method": "Query",
            "parameters": {
                "query": "关闭记事本"
            }
        },
        {
            "name": "系统命令",
            "method": "Query",
            "parameters": {
                "query": "关闭计算器"
            }
        }
    ]
    
    print(f"执行批量命令: {json.dumps(batch_commands, ensure_ascii=False)}")
    results = SystemCommands.handle_iot_commands(batch_commands)
    print(f"批量命令结果: {json.dumps(results, ensure_ascii=False)}")
    
    print("\n所有测试完成！")

async def main():
    """主函数"""
    try:
        await test_system_commands()
    except Exception as e:
        print(f"测试过程中出错: {e}")
    finally:
        print("测试结束")

if __name__ == "__main__":
    asyncio.run(main()) 