import asyncio
import logging
import json
from src.application import Application
from src.iot.thing_manager import ThingManager
from src.iot.things.system_manager import SystemManager
from src.constants.constants import DeviceState

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestOpenAppIoT")

async def simulate_llm_command():
    """模拟LLM生成的命令打开记事本"""
    # 获取应用实例
    app = Application.get_instance()
    
    # 手动初始化物联网设备
    thing_manager = ThingManager.get_instance()
    thing_manager.add_thing(SystemManager())
    logger.info("已手动添加 SystemManager 设备")
    
    # 创建一个模拟的 IoT 命令消息
    iot_message = {
        "type": "iot",
        "commands": [
            {
                "name": "SystemManager",
                "method": "OpenApplication",
                "parameters": {
                    "app_name": "记事本"
                }
            }
        ]
    }
    
    # 直接调用处理方法
    logger.info("正在模拟发送IoT命令打开记事本...")
    app._handle_iot_message(iot_message)
    
    # 等待操作完成
    await asyncio.sleep(3)
    
    # 查看设备状态
    states = json.loads(thing_manager.get_states_json())
    logger.info(f"当前设备状态: {states}")

if __name__ == "__main__":
    logger.info("开始测试通过IoT设备架构打开记事本...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(simulate_llm_command())
    logger.info("测试完成") 