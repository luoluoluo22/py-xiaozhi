import asyncio
import logging
import sys
import json
from src.application import Application

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("TestOpenAppIOT")

async def test_open_app_success():
    """测试通过IoT设备架构成功打开记事本"""
    app = Application()
    
    # 手动初始化IoT设备
    await app._initialize_iot_devices()
    
    # 构建打开记事本的IoT命令
    iot_command = {
        "name": "SystemManager",
        "method": "OpenApplication",
        "parameters": {
            "app_name": "记事本"
        }
    }
    
    logger.info(f"发送IoT命令: {iot_command}")
    
    # 发送命令到ThingManager
    result = await app.thing_manager.handle_command(iot_command)
    
    logger.info(f"命令执行结果: {result}")
    logger.info("测试完成！请检查记事本是否成功打开")
    
    # 等待5秒，让用户看到记事本窗口
    await asyncio.sleep(5)
    
    # 关闭记事本
    close_command = {
        "name": "SystemManager",
        "method": "CloseApplication",
        "parameters": {
            "app_name": "记事本"
        }
    }
    
    logger.info(f"发送关闭命令: {close_command}")
    result = await app.thing_manager.handle_command(close_command)
    logger.info(f"关闭命令执行结果: {result}")

async def test_open_app_failure():
    """测试打开不存在的应用程序"""
    app = Application()
    
    # 手动初始化IoT设备
    await app._initialize_iot_devices()
    
    # 构建打开不存在应用的IoT命令
    iot_command = {
        "name": "SystemManager",
        "method": "OpenApplication",
        "parameters": {
            "app_name": "不存在的应用程序XYZ"
        }
    }
    
    logger.info(f"发送IoT命令: {iot_command}")
    
    # 发送命令到ThingManager
    result = await app.thing_manager.handle_command(iot_command)
    
    logger.info(f"命令执行结果: {result}")
    logger.info("测试完成！应该收到失败信息")

async def run_tests():
    """运行所有测试"""
    logger.info("===== 开始测试: 打开存在的应用程序 =====")
    await test_open_app_success()
    
    logger.info("\n===== 开始测试: 打开不存在的应用程序 =====")
    await test_open_app_failure()

if __name__ == "__main__":
    asyncio.run(run_tests()) 