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
from src.utils.system_commands import SystemCommands

def test_single_iot_command():
    """测试单个IoT命令处理"""
    
    print("\n===== 测试打开记事本的IoT命令 =====")
    command = {
        "name": "系统命令",
        "method": "Query",
        "parameters": {
            "query": "打开记事本"
        }
    }
    
    # 输出命令
    print(f"执行命令: {json.dumps(command, ensure_ascii=False)}")
    
    # 执行命令
    result = SystemCommands.handle_iot_command(command)
    
    # 输出结果
    print(f"执行结果: {json.dumps(result, ensure_ascii=False)}")
    
    # 验证结果
    assert result["status"] == "success", "执行打开记事本命令失败"
    assert result["action"] == "open", "操作类型不是open"
    assert result["app_name"] == "记事本", "应用名称不匹配"
    assert result["success"] == True, "命令执行不成功"
    
    # 等待一会儿
    time.sleep(2)
    
    print("\n===== 测试关闭记事本的IoT命令 =====")
    command = {
        "name": "系统命令",
        "method": "Query",
        "parameters": {
            "query": "关闭记事本"
        }
    }
    
    # 输出命令
    print(f"执行命令: {json.dumps(command, ensure_ascii=False)}")
    
    # 执行命令
    result = SystemCommands.handle_iot_command(command)
    
    # 输出结果
    print(f"执行结果: {json.dumps(result, ensure_ascii=False)}")
    
    # 验证结果
    assert result["status"] == "success", "执行关闭记事本命令失败"
    assert result["action"] == "close", "操作类型不是close"
    assert result["app_name"] == "记事本", "应用名称不匹配"
    assert result["success"] == True, "命令执行不成功"

def test_batch_iot_commands():
    """测试批量IoT命令处理"""
    
    print("\n===== 测试批量IoT命令 =====")
    commands = [
        {
            "name": "系统命令",
            "method": "Query",
            "parameters": {
                "query": "打开记事本"
            }
        },
        {
            "name": "系统命令",
            "method": "Query",
            "parameters": {
                "query": "打开计算器"
            }
        }
    ]
    
    # 输出命令
    print(f"执行批量命令: {json.dumps(commands, ensure_ascii=False)}")
    
    # 执行命令
    results = SystemCommands.handle_iot_commands(commands)
    
    # 输出结果
    print(f"执行结果: {json.dumps(results, ensure_ascii=False)}")
    
    # 验证结果
    assert len(results) == 2, "结果数量不匹配"
    assert results[0]["status"] == "success", "第一个命令执行失败"
    assert results[1]["status"] == "success", "第二个命令执行失败"
    
    # 等待一会儿
    time.sleep(2)
    
    # 关闭打开的应用
    close_commands = [
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
    
    # 执行关闭命令
    close_results = SystemCommands.handle_iot_commands(close_commands)
    
    # 输出结果
    print(f"关闭应用结果: {json.dumps(close_results, ensure_ascii=False)}")

def test_error_handling():
    """测试错误处理"""
    
    print("\n===== 测试错误处理 =====")
    
    # 测试无效命令
    print("测试无效命令格式")
    result = SystemCommands.handle_iot_command({})
    print(f"结果: {json.dumps(result, ensure_ascii=False)}")
    assert result["status"] == "error", "应该返回错误状态"
    
    # 测试不支持的命令类型
    print("测试不支持的命令类型")
    result = SystemCommands.handle_iot_command({
        "name": "未知命令",
        "method": "Query",
        "parameters": {
            "query": "打开记事本"
        }
    })
    print(f"结果: {json.dumps(result, ensure_ascii=False)}")
    assert result["status"] == "error", "应该返回错误状态"
    
    # 测试不支持的方法
    print("测试不支持的方法")
    result = SystemCommands.handle_iot_command({
        "name": "系统命令",
        "method": "未知方法",
        "parameters": {
            "query": "打开记事本"
        }
    })
    print(f"结果: {json.dumps(result, ensure_ascii=False)}")
    assert result["status"] == "error", "应该返回错误状态"
    
    # 测试无效的查询命令
    print("测试无效的查询命令")
    result = SystemCommands.handle_iot_command({
        "name": "系统命令",
        "method": "Query",
        "parameters": {
            "query": "无效命令"
        }
    })
    print(f"结果: {json.dumps(result, ensure_ascii=False)}")
    assert result["status"] == "error", "应该返回错误状态"

def main():
    """主函数"""
    print("开始测试IoT命令功能...")
    
    # 测试单个IoT命令
    test_single_iot_command()
    
    # 测试批量IoT命令
    test_batch_iot_commands()
    
    # 测试错误处理
    test_error_handling()
    
    print("\n所有测试通过！")

if __name__ == "__main__":
    main() 