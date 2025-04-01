import logging
import threading
import time
from datetime import datetime, timedelta
import re
from typing import Dict, Any, Optional, List, Tuple
import os
from winotify import Notification, audio

# 配置日志
logger = logging.getLogger(__name__)

class ReminderManager:
    """提醒管理工具类"""
    
    # 存储当前活跃的提醒
    _active_reminders = {}
    _reminder_counter = 0
    
    @staticmethod
    def _parse_time_string(time_str: str) -> Tuple[int, str]:
        """
        解析时间字符串，如"3分钟"、"5秒"、"1小时30分钟"等
        
        Args:
            time_str: 时间字符串
            
        Returns:
            Tuple[int, str]: (秒数, 单位描述)
        """
        # 移除所有空格和"后"字
        time_str = time_str.replace(" ", "").replace("后", "").lower()
        logger.info(f"解析时间字符串: {time_str}")
        
        # 定义正则表达式模式匹配时间
        patterns = [
            # 小时
            (r'(\d+)(?:小时|h|hour|hours)', 3600),
            # 分钟
            (r'(\d+)(?:分钟|分|min|minute|minutes|m)', 60),
            # 秒钟
            (r'(\d+)(?:秒钟|秒|s|sec|second|seconds)', 1)
        ]
        
        total_seconds = 0
        unit_description = []
        
        # 检查每种时间单位
        for pattern, multiplier in patterns:
            matches = re.findall(pattern, time_str, re.IGNORECASE)
            for match in matches:
                try:
                    value = int(match)
                    total_seconds += value * multiplier
                    
                    # 构建单位描述
                    if multiplier == 3600:
                        unit_description.append(f"{value}小时")
                    elif multiplier == 60:
                        unit_description.append(f"{value}分钟")
                    else:
                        unit_description.append(f"{value}秒")
                        
                except ValueError:
                    continue
        
        # 如果没有匹配到任何时间单位，尝试将整个字符串解析为秒数
        if total_seconds == 0:
            try:
                # 移除非数字字符
                digits_only = re.sub(r'\D', '', time_str)
                if digits_only:
                    total_seconds = int(digits_only)
                    unit_description = [f"{total_seconds}秒"]
            except ValueError:
                pass
        
        logger.info(f"解析结果: {total_seconds}秒, 描述: {''.join(unit_description)}")
        return total_seconds, "".join(unit_description)
    
    @staticmethod
    def _show_notification(title: str, message: str, duration: str = "long"):
        """
        显示Windows系统通知
        
        Args:
            title: 通知标题
            message: 通知内容
            duration: 通知持续时间
        """
        try:
            toast = Notification(
                app_id="提醒助手",
                title=title,
                msg=message,
                duration=duration
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
            
            logger.info(f"已显示通知: {title} - {message}")
            return True
            
        except Exception as e:
            logger.error(f"显示通知失败: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def _reminder_thread(reminder_id: int, delay_seconds: int, title: str, message: str, repeat: bool = False, repeat_interval: int = 0):
        """
        提醒线程，等待指定时间后显示通知
        
        Args:
            reminder_id: 提醒ID
            delay_seconds: 延迟秒数
            title: 通知标题
            message: 通知内容
            repeat: 是否重复提醒
            repeat_interval: 重复间隔（秒）
        """
        logger.info(f"设置提醒: ID={reminder_id}, 延迟={delay_seconds}秒, 标题='{title}', 内容='{message}'")
        
        try:
            # 等待指定时间
            time.sleep(delay_seconds)
            
            # 显示通知
            ReminderManager._show_notification("⏰ 提醒时间到了", message)
            
            # 如果设置了重复提醒，继续循环
            while repeat and reminder_id in ReminderManager._active_reminders:
                time.sleep(repeat_interval)
                ReminderManager._show_notification(title, message)
                
        except Exception as e:
            logger.error(f"提醒线程出错: {str(e)}", exc_info=True)
        finally:
            # 如果不是重复提醒，或者提醒已被取消，从活跃提醒中移除
            if not repeat or reminder_id not in ReminderManager._active_reminders:
                ReminderManager._remove_reminder(reminder_id)
                
            # 更新提醒状态为已完成
            if reminder_id in ReminderManager._active_reminders:
                ReminderManager._active_reminders[reminder_id]["status"] = "completed"
    
    @staticmethod
    def _remove_reminder(reminder_id: int) -> bool:
        """
        移除指定ID的提醒
        
        Args:
            reminder_id: 提醒ID
            
        Returns:
            bool: 操作是否成功
        """
        if reminder_id in ReminderManager._active_reminders:
            logger.info(f"移除提醒: ID={reminder_id}")
            ReminderManager._active_reminders.pop(reminder_id, None)
            return True
        return False
    
    @staticmethod
    def set_reminder(time_str: str, message: str, title: str = "提醒") -> Dict[str, Any]:
        """
        设置一个提醒
        
        Args:
            time_str: 时间字符串，如"3分钟"、"5秒"、"1小时30分钟"
            message: 提醒内容
            title: 提醒标题
            
        Returns:
            Dict: 包含设置结果的字典
        """
        try:
            # 解析时间字符串
            seconds, time_description = ReminderManager._parse_time_string(time_str)
            
            if seconds <= 0:
                logger.error(f"无效的时间字符串: {time_str}")
                return {
                    "status": "error",
                    "message": f"无效的时间设置: {time_str}"
                }
            
            # 生成提醒ID
            ReminderManager._reminder_counter += 1
            reminder_id = ReminderManager._reminder_counter
            
            # 计算提醒时间
            reminder_time = datetime.now() + timedelta(seconds=seconds)
            
            # 创建并启动提醒线程
            reminder_thread = threading.Thread(
                target=ReminderManager._reminder_thread,
                args=(reminder_id, seconds, title, message),
                daemon=True
            )
            reminder_thread.start()
            
            # 存储提醒信息
            ReminderManager._active_reminders[reminder_id] = {
                "id": reminder_id,
                "message": message,
                "title": title,
                "time": reminder_time,
                "thread": reminder_thread,
                "status": "active"
            }
            
            logger.info(f"成功设置提醒: ID={reminder_id}, 时间={time_description}后, 内容='{message}'")
            
            return {
                "status": "success",
                "message": f"已设置{time_description}后提醒: {message}",
                "reminder_id": reminder_id,
                "reminder_time": reminder_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"设置提醒失败: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"设置提醒失败: {str(e)}"
            }
    
    @staticmethod
    def cancel_reminder(reminder_id: int) -> Dict[str, Any]:
        """
        取消指定ID的提醒
        
        Args:
            reminder_id: 提醒ID
            
        Returns:
            Dict: 包含取消结果的字典
        """
        try:
            success = ReminderManager._remove_reminder(reminder_id)
            
            if success:
                return {
                    "status": "success",
                    "message": f"已取消提醒 (ID: {reminder_id})"
                }
            else:
                return {
                    "status": "error",
                    "message": f"未找到提醒 (ID: {reminder_id})"
                }
                
        except Exception as e:
            logger.error(f"取消提醒失败: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"取消提醒失败: {str(e)}"
            }
    
    @staticmethod
    def list_reminders() -> Dict[str, Any]:
        """
        列出所有活跃的提醒
        
        Returns:
            Dict: 包含提醒列表的字典
        """
        try:
            reminders = []
            now = datetime.now()
            
            for reminder_id, reminder in ReminderManager._active_reminders.items():
                remaining_seconds = (reminder["time"] - now).total_seconds()
                
                if remaining_seconds > 0 or reminder["status"] == "completed":
                    remaining_time = ReminderManager._format_remaining_time(remaining_seconds)
                    
                    reminders.append({
                        "id": reminder_id,
                        "message": reminder["message"],
                        "time": reminder["time"].strftime("%Y-%m-%d %H:%M:%S"),
                        "remaining": remaining_time,
                        "status": reminder["status"]
                    })
            
            return {
                "status": "success",
                "message": f"找到 {len(reminders)} 个提醒",
                "reminders": reminders
            }
            
        except Exception as e:
            logger.error(f"列出提醒失败: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"列出提醒失败: {str(e)}"
            }
    
    @staticmethod
    def _format_remaining_time(seconds: float) -> str:
        """
        格式化剩余时间
        
        Args:
            seconds: 剩余秒数
            
        Returns:
            str: 格式化后的时间字符串
        """
        if seconds <= 0:
            return "已完成"
            
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}秒")
            
        return "".join(parts)
    
    @staticmethod
    def set_countdown(seconds: int, message: str = "倒计时结束") -> Dict[str, Any]:
        """
        设置倒计时
        
        Args:
            seconds: 倒计时秒数
            message: 倒计时结束提示信息
            
        Returns:
            Dict: 包含设置结果的字典
        """
        return ReminderManager.set_reminder(str(seconds), message, "倒计时") 