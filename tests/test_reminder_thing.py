import unittest
from datetime import datetime, timedelta
from src.things.reminder_thing import ReminderThing
import time

class TestReminderThing(unittest.TestCase):
    def setUp(self):
        """测试前的初始化工作"""
        self.reminder = ReminderThing("test_reminder_001")
        self.reminder.initialize()

    def tearDown(self):
        """测试后的清理工作"""
        self.reminder.cleanup()

    def test_initialization(self):
        """测试初始化是否正确"""
        self.assertEqual(self.reminder.name, "ReminderThing")
        self.assertEqual(self.reminder.thing_id, "test_reminder_001")
        self.assertEqual(len(self.reminder.reminders), 0)

    def test_set_reminder(self):
        """测试设置提醒功能"""
        # 设置一个5分钟后的提醒
        future_time = datetime.now() + timedelta(minutes=5)
        result = self.reminder.process_command("set", {
            "time": future_time,
            "message": "测试提醒"
        })
        
        self.assertEqual(result["status"], "success")
        self.assertTrue("提醒已设置" in result["message"])
        self.assertEqual(len(self.reminder.reminders), 1)

    def test_list_reminders(self):
        """测试列出所有提醒"""
        # 先设置两个提醒
        future_time1 = datetime.now() + timedelta(minutes=5)
        future_time2 = datetime.now() + timedelta(minutes=10)
        
        self.reminder.process_command("set", {
            "time": future_time1,
            "message": "提醒1"
        })
        self.reminder.process_command("set", {
            "time": future_time2,
            "message": "提醒2"
        })
        
        # 测试列出提醒
        result = self.reminder.process_command("list", {})
        self.assertTrue("reminders" in result)
        self.assertEqual(len(result["reminders"]), 2)

    def test_invalid_command(self):
        """测试无效命令处理"""
        result = self.reminder.process_command("invalid_command", {})
        self.assertEqual(result["status"], "error")
        self.assertTrue("未知命令" in result["message"])

    def test_reminder_status(self):
        """测试提醒状态"""
        future_time = datetime.now() + timedelta(minutes=5)
        self.reminder.process_command("set", {
            "time": future_time,
            "message": "状态测试"
        })
        
        # 检查设备状态
        status = self.reminder.get_status()
        self.assertTrue("status" in status)
        self.assertEqual(status["status"], "online")

    def test_five_second_reminder(self):
        """测试5秒后的提醒功能"""
        # 设置5秒后的提醒
        reminder_time = datetime.now() + timedelta(seconds=5)
        message = "5秒后的测试提醒"
        
        result = self.reminder.process_command("set", {
            "time": reminder_time,
            "message": message
        })
        
        self.assertEqual(result["status"], "success")
        
        # 等待6秒，确保提醒被触发
        time.sleep(6)
        
        # 检查提醒状态是否已更新为completed
        result = self.reminder.process_command("list", {})
        reminder = list(result["reminders"].values())[0]
        self.assertEqual(reminder["status"], "completed")
        self.assertEqual(reminder["message"], message)

if __name__ == '__main__':
    unittest.main() 