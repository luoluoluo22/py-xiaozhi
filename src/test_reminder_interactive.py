from things import ReminderThing
import time

def main():
    print("=== 提醒功能交互式测试 ===")
    
    # 创建提醒管理器
    reminder = ReminderThing("test_reminder")
    reminder.initialize()
    
    try:
        # 设置5秒后的提醒
        message = "这是一个5秒后的提醒！"
        
        print("\n[设置提醒]")
        result = reminder.process_command("SetReminder", {
            "time_str": "5秒后",
            "message": message
        })
        print(f"设置结果: {result.get('message', '成功')}")
        print(f"请等待5秒，马上就会看到提醒...")
        
        # 等待7秒，确保能看到提醒
        time.sleep(7)
        
        # 显示所有提醒的状态
        print("\n[提醒列表]")
        result = reminder.process_command("list", {})
        reminders = result.get("reminders", [])
        for r in reminders:
            print(f"提醒:")
            print(f"  消息: {r.get('message')}")
            print(f"  状态: {r.get('status')}")
            print(f"  时间: {r.get('time')}")
            
    finally:
        reminder.cleanup()

if __name__ == "__main__":
    main() 