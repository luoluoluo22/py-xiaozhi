from src.iot.thing import Thing, Parameter, ValueType
import logging
from typing import Dict, Any
import asyncio
from src.utils.reminder import ReminderManager
from src.utils.reminder_commands import process_reminder_command, process_countdown_command
import re

logger = logging.getLogger("ReminderThing")

class ReminderThing(Thing):
    """
    提醒管理组件
    
    提供设置提醒、取消提醒、查看提醒等功能。
    """
    
    def __init__(self):
        """初始化提醒管理器"""
        super().__init__(
            "ReminderManager", 
            "提醒管理组件，支持设置提醒、倒计时等功能"
        )
        
        # 获取应用程序实例
        from src.application import Application
        self.app = Application.get_instance()
        
        logger.info("提醒管理器初始化完成")
        
        # 注册属性和方法
        self._register_properties()
        self._register_methods()
    
    def _register_properties(self):
        """注册提醒系统属性"""
        self.add_property(
            "ActiveReminders",
            "当前活跃的提醒数量",
            lambda: len(ReminderManager._active_reminders)
        )
    
    def _register_methods(self):
        """注册提醒系统方法"""
        self.add_method(
            "SetReminder", 
            "设置一个提醒",
            [
                Parameter("time_str", "时间字符串，如'10s后'、'5分钟后'等", ValueType.STRING, True),
                Parameter("message", "提醒内容", ValueType.STRING, True)
            ],
            lambda params: self._set_reminder(
                params["time_str"].get_value(), 
                params["message"].get_value()
            )
        )
        
        self.add_method(
            "CancelReminder", 
            "取消一个提醒", 
            [Parameter("reminder_id", "提醒ID", ValueType.NUMBER, True)],
            lambda params: self._cancel_reminder(params["reminder_id"].get_value())
        )
        
        self.add_method(
            "ListReminders", 
            "列出所有活跃的提醒", 
            [],
            lambda params: self._list_reminders()
        )
        
        self.add_method(
            "Query", 
            "处理提醒相关查询", 
            [Parameter("query", "查询内容", ValueType.STRING, True)],
            lambda params: self._process_reminder_query(params["query"].get_value())
        )
    
    def _set_reminder(self, time_str: str, message: str) -> Dict[str, Any]:
        """
        设置提醒
        
        参数:
            time_str: 时间字符串，如"10s后"、"5分钟后"等
            message: 提醒内容
            
        返回:
            Dict[str, Any]: 操作结果
        """
        try:
            logger.info(f"提醒管理器正在设置提醒: 时间={time_str}, 内容={message}")
            result = ReminderManager.set_reminder(time_str, message)
            
            # 直接向应用程序反馈成功信息
            if self.app:
                try:
                    # 使用异步方式发送语音反馈
                    time_desc = result.get("message", "").replace("成功设置提醒: ", "")
                    asyncio.run_coroutine_threadsafe(
                        self.app._speak(f"好的，{time_desc}"),
                        self.app.loop
                    )
                except Exception as e:
                    logger.error(f"发送反馈消息失败: {e}")
            
            # 向服务器发送操作结果状态更新
            self.app.schedule(lambda: self.app._update_iot_states())
            
            return result
            
        except Exception as e:
            logger.error(f"设置提醒失败: {str(e)}")
            error_result = {
                "status": "error", 
                "message": f"设置提醒时出错: {str(e)}"
            }
            
            # 向应用程序反馈错误
            if self.app:
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.app._speak(f"抱歉，设置提醒时出现错误"),
                        self.app.loop
                    )
                except Exception as feedback_err:
                    logger.error(f"发送错误反馈消息失败: {feedback_err}")
                    
            return error_result
    
    def _cancel_reminder(self, reminder_id: int) -> Dict[str, Any]:
        """
        取消提醒
        
        参数:
            reminder_id: 提醒ID
            
        返回:
            Dict[str, Any]: 操作结果
        """
        try:
            logger.info(f"提醒管理器正在取消提醒: ID={reminder_id}")
            result = ReminderManager.cancel_reminder(reminder_id)
            
            # 直接向应用程序反馈成功信息
            if self.app and result.get("status") == "success":
                try:
                    # 使用异步方式发送语音反馈
                    asyncio.run_coroutine_threadsafe(
                        self.app._speak(f"已取消提醒"),
                        self.app.loop
                    )
                except Exception as e:
                    logger.error(f"发送反馈消息失败: {e}")
            
            # 向服务器发送操作结果状态更新
            self.app.schedule(lambda: self.app._update_iot_states())
            
            return result
            
        except Exception as e:
            logger.error(f"取消提醒失败: {str(e)}")
            error_result = {
                "status": "error", 
                "message": f"取消提醒时出错: {str(e)}"
            }
            
            # 向应用程序反馈错误
            if self.app:
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.app._speak(f"抱歉，取消提醒时出现错误"),
                        self.app.loop
                    )
                except Exception as feedback_err:
                    logger.error(f"发送错误反馈消息失败: {feedback_err}")
            
            return error_result
    
    def _list_reminders(self) -> Dict[str, Any]:
        """
        列出所有活跃的提醒
        
        返回:
            Dict[str, Any]: 包含提醒列表的结果
        """
        try:
            logger.info("提醒管理器正在列出所有活跃提醒")
            result = ReminderManager.list_reminders()
            
            # 直接向应用程序反馈成功信息
            if self.app:
                try:
                    # 使用异步方式发送语音反馈
                    reminders = result.get("reminders", [])
                    count = len(reminders)
                    
                    if count > 0:
                        reminders_text = "、".join([f"'{r['message']}'({r['remaining']}后)" for r in reminders[:3]])
                        if count > 3:
                            reminders_text += f"等{count}个提醒"
                        
                        asyncio.run_coroutine_threadsafe(
                            self.app._speak(f"您当前有{count}个活跃提醒: {reminders_text}"),
                            self.app.loop
                        )
                    else:
                        asyncio.run_coroutine_threadsafe(
                            self.app._speak("您当前没有活跃的提醒"),
                            self.app.loop
                        )
                except Exception as e:
                    logger.error(f"发送反馈消息失败: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"列出提醒失败: {str(e)}")
            error_result = {
                "status": "error", 
                "message": f"列出提醒时出错: {str(e)}"
            }
            
            # 向应用程序反馈错误
            if self.app:
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.app._speak(f"抱歉，获取提醒列表时出现错误"),
                        self.app.loop
                    )
                except Exception as feedback_err:
                    logger.error(f"发送错误反馈消息失败: {feedback_err}")
            
            return error_result
    
    def _process_reminder_query(self, query: str) -> Dict[str, Any]:
        """
        处理提醒相关查询
        
        参数:
            query: 查询字符串
            
        返回:
            Dict[str, Any]: 操作结果
        """
        try:
            logger.info(f"提醒管理器处理查询: {query}")
            
            # 检查是否是列出提醒的查询
            if re.search(r'(列出|查看|显示|有哪些).*?(提醒|闹钟)', query):
                return self._list_reminders()
            
            # 检查是否是取消提醒的查询
            cancel_match = re.search(r'(取消|关闭|停止).*?(提醒|闹钟).*?(\d+)', query)
            if cancel_match:
                reminder_id = int(cancel_match.group(3))
                return self._cancel_reminder(reminder_id)
            
            # 处理提醒命令
            if "提醒" in query or "闹钟" in query or "定时" in query:
                # 使用提醒命令处理模块处理
                logger.info(f"检测到提醒命令: {query}")
                result = process_reminder_command(query)
                
                # 处理成功结果
                if result.get("status") == "success":
                    # 直接向应用程序反馈成功信息
                    if self.app:
                        try:
                            time_desc = result.get("message", "").replace("成功设置提醒: ", "")
                            asyncio.run_coroutine_threadsafe(
                                self.app._speak(f"好的，{time_desc}"),
                                self.app.loop
                            )
                        except Exception as e:
                            logger.error(f"发送反馈消息失败: {e}")
                
                return result
                
            # 处理倒计时命令
            elif "倒计时" in query:
                # 使用倒计时命令处理模块处理
                logger.info(f"检测到倒计时命令: {query}")
                result = process_countdown_command(query)
                
                # 处理成功结果
                if result.get("status") == "success":
                    # 直接向应用程序反馈成功信息
                    if self.app:
                        try:
                            time_desc = result.get("message", "").replace("成功设置提醒: ", "")
                            asyncio.run_coroutine_threadsafe(
                                self.app._speak(f"好的，{time_desc}"),
                                self.app.loop
                            )
                        except Exception as e:
                            logger.error(f"发送反馈消息失败: {e}")
                
                return result
            
            # 处理时间+后的格式（如"10s后"、"5分钟后"等）
            elif re.search(r'\d+\s*(?:秒钟|秒|分钟|分|小时|s|sec|m|min|h|hour)后', query, re.IGNORECASE):
                logger.info(f"检测到时间提醒命令: {query}")
                result = process_reminder_command(query)
                
                # 处理成功结果
                if result.get("status") == "success":
                    # 直接向应用程序反馈成功信息
                    if self.app:
                        try:
                            time_desc = result.get("message", "").replace("成功设置提醒: ", "")
                            asyncio.run_coroutine_threadsafe(
                                self.app._speak(f"好的，{time_desc}"),
                                self.app.loop
                            )
                        except Exception as e:
                            logger.error(f"发送反馈消息失败: {e}")
                
                return result
                
            else:
                logger.warning(f"未识别的提醒查询: {query}")
                return {
                    "status": "error",
                    "message": f"未识别的提醒查询: {query}"
                }
                
        except Exception as e:
            logger.error(f"处理提醒查询失败: {str(e)}")
            error_result = {
                "status": "error", 
                "message": f"处理提醒查询时出错: {str(e)}"
            }
            
            # 向应用程序反馈错误
            if self.app:
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.app._speak(f"抱歉，处理提醒请求时出现错误"),
                        self.app.loop
                    )
                except Exception as feedback_err:
                    logger.error(f"发送错误反馈消息失败: {feedback_err}")
            
            return error_result 