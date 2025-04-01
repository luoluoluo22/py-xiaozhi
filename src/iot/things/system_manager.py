from src.application import Application
from src.iot.thing import Thing, Parameter, ValueType
from src.utils.system_commands import SystemCommands
import logging
from typing import Dict, Any
import asyncio

logger = logging.getLogger("SystemManager")

class SystemManager(Thing):
    """
    系统管理组件
    
    提供系统级命令，如打开/关闭应用程序、调整系统设置等功能。
    """
    
    def __init__(self):
        """初始化系统管理器"""
        super().__init__(
            "SystemManager", 
            "系统管理组件，支持应用程序控制"
        )
        
        # 获取应用程序实例
        self.app = Application.get_instance()
        
        # 初始化系统命令工具
        self.system_commands = SystemCommands()
        
        logger.info("系统管理器初始化完成")
        
        # 注册属性和方法
        self._register_properties()
        self._register_methods()
    
    def _register_properties(self):
        """注册系统属性"""
        # 暂时没有需要注册的属性
        pass
    
    def _register_methods(self):
        """注册系统方法"""
        self.add_method(
            "OpenApplication", 
            "打开指定应用程序",
            [Parameter("app_name", "应用程序名称", ValueType.STRING, True)],
            lambda params: self._open_application(params["app_name"].get_value())
        )
        
        self.add_method(
            "CloseApplication", 
            "关闭指定应用程序", 
            [Parameter("app_name", "应用程序名称", ValueType.STRING, True)],
            lambda params: self._close_application(params["app_name"].get_value())
        )
    
    def _open_application(self, app_name: str) -> Dict[str, Any]:
        """
        打开指定应用程序
        
        参数:
            app_name: 应用程序名称
            
        返回:
            Dict[str, Any]: 操作结果
        """
        try:
            logger.info(f"系统管理器正在打开应用: {app_name}")
            success = SystemCommands.open_application(app_name)
            
            if success:
                result = {
                    "status": "success", 
                    "message": f"已成功打开 {app_name}",
                    "action": "open",
                    "app_name": app_name
                }
                
                # 直接向应用程序反馈成功信息
                if self.app:
                    try:
                        # 使用异步方式发送语音反馈
                        asyncio.run_coroutine_threadsafe(
                            self.app._speak(f"已为您打开{app_name}"),
                            self.app.loop
                        )
                    except Exception as e:
                        logger.error(f"发送反馈消息失败: {e}")
            else:
                result = {
                    "status": "error", 
                    "message": f"无法打开 {app_name}",
                    "action": "open",
                    "app_name": app_name
                }
                
                # 直接向应用程序反馈错误信息
                if self.app:
                    try:
                        # 使用异步方式发送语音反馈
                        asyncio.run_coroutine_threadsafe(
                            self.app._speak(f"抱歉，无法打开{app_name}，请检查应用名称是否正确"),
                            self.app.loop
                        )
                    except Exception as e:
                        logger.error(f"发送错误反馈消息失败: {e}")
            
            # 向服务器发送操作结果状态更新
            self.app.schedule(lambda: self.app._update_iot_states())
            
            return result
            
        except Exception as e:
            logger.error(f"打开应用程序失败: {str(e)}")
            error_result = {
                "status": "error", 
                "message": f"打开应用程序时出错: {str(e)}",
                "action": "open",
                "app_name": app_name
            }
            
            # 向应用程序反馈错误
            if self.app:
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.app._speak(f"抱歉，打开{app_name}时出现错误"),
                        self.app.loop
                    )
                except Exception as feedback_err:
                    logger.error(f"发送错误反馈消息失败: {feedback_err}")
                    
            return error_result
    
    def _close_application(self, app_name: str) -> Dict[str, Any]:
        """
        关闭指定应用程序
        
        参数:
            app_name: 应用程序名称
            
        返回:
            Dict[str, Any]: 操作结果
        """
        try:
            logger.info(f"系统管理器正在关闭应用: {app_name}")
            success = SystemCommands.close_application(app_name)
            
            if success:
                result = {
                    "status": "success", 
                    "message": f"已成功关闭 {app_name}",
                    "action": "close",
                    "app_name": app_name
                }
                
                # 直接向应用程序反馈成功信息
                if self.app:
                    try:
                        # 使用异步方式发送语音反馈
                        asyncio.run_coroutine_threadsafe(
                            self.app._speak(f"已为您关闭{app_name}"),
                            self.app.loop
                        )
                    except Exception as e:
                        logger.error(f"发送反馈消息失败: {e}")
            else:
                result = {
                    "status": "error", 
                    "message": f"无法关闭 {app_name}",
                    "action": "close",
                    "app_name": app_name
                }
                
                # 直接向应用程序反馈错误信息
                if self.app:
                    try:
                        # 使用异步方式发送语音反馈
                        asyncio.run_coroutine_threadsafe(
                            self.app._speak(f"抱歉，无法关闭{app_name}，可能该应用未在运行"),
                            self.app.loop
                        )
                    except Exception as e:
                        logger.error(f"发送错误反馈消息失败: {e}")
            
            # 向服务器发送操作结果状态更新
            self.app.schedule(lambda: self.app._update_iot_states())
            
            return result
            
        except Exception as e:
            logger.error(f"关闭应用程序失败: {str(e)}")
            error_result = {
                "status": "error", 
                "message": f"关闭应用程序时出错: {str(e)}",
                "action": "close",
                "app_name": app_name
            }
            
            # 向应用程序反馈错误
            if self.app:
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.app._speak(f"抱歉，关闭{app_name}时出现错误"),
                        self.app.loop
                    )
                except Exception as feedback_err:
                    logger.error(f"发送错误反馈消息失败: {feedback_err}")
            
            return error_result 