from winotify import Notification, audio
import time

def test_notification():
    # 创建通知
    toast = Notification(
        app_id="测试通知",
        title="测试标题",
        msg="这是一条测试消息",
        duration="short"
    )
    
    # 设置声音
    toast.set_audio(audio.Default, loop=False)
    
    print("正在发送通知...")
    toast.show()
    print("通知已发送，请查看右下角通知栏")
    
    # 等待5秒
    time.sleep(5)
    
    # 发送第二条通知
    toast2 = Notification(
        app_id="测试通知",
        title="第二条通知",
        msg="如果你能看到这条通知，说明通知系统正常工作",
        duration="long"
    )
    toast2.set_audio(audio.Default, loop=False)
    toast2.show()
    print("第二条通知已发送")

if __name__ == "__main__":
    test_notification() 