from datetime import datetime
import time
import threading
from winotify import Notification, audio
import os
import queue
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.reminder import ReminderManager

logger = logging.getLogger(__name__)

class Thing:
    """IoT设备基类"""
    
    def __init__(self, thing_id: str):
        """初始化IoT设备
        
        Args:
            thing_id: 设备唯一标识符
        """
        self.thing_id = thing_id
        self.name = "BaseThing"
        self.description = "基础IoT设备"

    def initialize(self) -> bool:
        """初始化设备
        
        Returns:
            bool: 初始化是否成功
        """
        return True

    def get_status(self) -> dict:
        """获取设备状态
        
        Returns:
            dict: 设备状态信息
        """
        return {"status": "unknown"}

    def process_command(self, command: str, params: dict) -> dict:
        """处理接收到的命令
        
        Args:
            command: 命令名称
            params: 命令参数
            
        Returns:
            dict: 命令执行结果
        """
        return {"status": "error", "message": "命令未实现"} 

    def cleanup(self):
        """清理资源"""
        pass


class ReminderThing(Thing):
    """提醒功能管理器"""
    
    def __init__(self, thing_id: str):
        """初始化提醒管理器
        
        Args:
            thing_id: 设备唯一标识符
        """
        super().__init__(thing_id)
        self.name = "ReminderThing"
        self.description = "提醒功能管理器"
        
        # 通知队列和处理线程
        self._notification_queue = queue.Queue()
        self._notification_thread = None
        self._stop_notification = False

    def initialize(self) -> bool:
        """初始化设备
        
        Returns:
            bool: 初始化是否成功
        """
        self._start_notification_thread()
        return True

    def _start_notification_thread(self):
        """启动通知处理线程"""
        self._stop_notification = False
        self._notification_thread = threading.Thread(target=self._process_notifications)
        self._notification_thread.daemon = True
        self._notification_thread.start()

    def _process_notifications(self):
        """处理通知队列的循环"""
        while not self._stop_notification:
            try:
                # 从队列获取通知信息，设置超时以便能够响应停止信号
                try:
                    title, msg, duration = self._notification_queue.get(timeout=1)
                except queue.Empty:
                    continue

                # 创建并显示通知
                try:
                    toast = Notification(
                        app_id="提醒助手",
                        title=title,
                        msg=msg,
                        duration=duration
                    )
                    toast.set_audio(audio.Default, loop=False)
                    toast.show()
                    
                    # 记录通知发送
                    logger.info(f"已发送通知 - 标题: {title}, 内容: {msg}")
                    
                    # 短暂延时确保通知显示
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"显示通知失败: {e}")
                
                finally:
                    # 标记任务完成
                    self._notification_queue.task_done()
                    
            except Exception as e:
                logger.error(f"处理通知时出错: {e}")
                time.sleep(1)  # 发生错误时等待一下

    def _show_notification(self, title: str, msg: str, duration: str = "short"):
        """将通知加入队列
        
        Args:
            title: 通知标题
            msg: 通知内容
            duration: 通知持续时间
        """
        try:
            self._notification_queue.put((title, msg, duration))
            logger.info(f"通知已加入队列 - 标题: {title}")
        except Exception as e:
            logger.error(f"添加通知到队列失败: {e}")

    def process_command(self, command: str, params: dict) -> dict:
        """处理接收到的命令
        
        Args:
            command: 命令名称
            params: 命令参数
            
        Returns:
            dict: 命令执行结果
        """
        try:
            logger.info(f"处理命令: {command}, 参数: {params}")
            
            if command == "SetReminder":
                # 使用 ReminderManager 设置提醒
                time_str = params.get("time_str")
                message = params.get("message", "")
                
                if not time_str:
                    raise ValueError("缺少时间参数")
                if not message:
                    raise ValueError("缺少提醒内容")
                
                result = ReminderManager.set_reminder(time_str, message)
                
                # 如果设置成功，显示通知
                if result.get("status") == "success":
                    self._show_notification(
                        "✅ 提醒已设置",
                        f'将在 {result.get("reminder_time", "稍后")} 提醒您：\n{message}'
                    )
                    
                return result
                
            elif command == "list":
                return ReminderManager.list_reminders()
                
            else:
                logger.warning(f"未知命令: {command}")
                return {"status": "error", "message": f"未知命令: {command}"}
                
        except Exception as e:
            logger.error(f"处理命令失败: {e}")
            return {
                "status": "error",
                "message": f"处理命令失败: {str(e)}"
            }

    def get_status(self) -> dict:
        """获取设备状态
        
        Returns:
            dict: 设备状态信息
        """
        reminders = ReminderManager.list_reminders()
        active_count = len([r for r in reminders.get("reminders", []) 
                          if r.get("status") == "active"])
        
        return {
            "status": "online",
            "active_reminders": active_count
        }

    def cleanup(self):
        """清理资源"""
        self._stop_notification = True
        
        if self._notification_thread:
            self._notification_thread.join(timeout=2) 