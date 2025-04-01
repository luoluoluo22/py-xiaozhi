import logging
import time
from src.utils.system_commands import SystemCommands

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_open_close_apps():
    """测试打开和关闭新添加的应用程序"""
    
    # 测试应用列表 - 根据实际安装的应用程序选择几个测试
    apps_to_test = [
        "计算器",
        "微信",
        "网易云音乐",
        "坚果云",
        "everything",
        "chrome"
    ]
    
    results = {}
    
    for app in apps_to_test:
        try:
            logger.info(f"测试打开应用: {app}")
            open_result = SystemCommands.open_application(app)
            results[app] = {"open": open_result}
            
            # 等待应用启动
            time.sleep(3)
            
            logger.info(f"测试关闭应用: {app}")
            close_result = SystemCommands.close_application(app)
            results[app]["close"] = close_result
            
            # 等待一下再进行下一个测试
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"测试应用 {app} 时出错: {e}")
            results[app] = {"error": str(e)}
    
    # 打印结果摘要
    logger.info("测试结果摘要:")
    for app, result in results.items():
        if "error" in result:
            logger.info(f"应用 {app}: 出错 - {result['error']}")
        else:
            logger.info(f"应用 {app}: 打开={'成功' if result.get('open') else '失败'}, 关闭={'成功' if result.get('close') else '失败'}")

if __name__ == "__main__":
    test_open_close_apps() 