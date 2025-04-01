import os
import sys
import logging
import time

# 添加src目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# 导入必要的类
from src.utils.system_commands import SystemCommands
from src.utils.app_finder import search_app, find_app_in_start_menu

def test_local_app_search():
    """测试本地应用程序搜索功能"""
    
    # 首先关闭记事本，以防之前的测试没有正常关闭
    print("\n===== 清理环境：关闭记事本 =====")
    SystemCommands.close_application("notepad")
    
    # 测试搜索并打开常见应用程序 - 微信
    print("\n===== 测试搜索并打开微信 =====")
    app_name = "微信"
    
    # 搜索应用程序
    search_result = search_app(app_name)
    if search_result:
        print(f"找到应用程序: {search_result['name']}")
        print(f"匹配度: {search_result['match_score']}%")
        
        if 'executable_path' in search_result:
            print(f"可执行程序路径: {search_result['executable_path']}")
            
            # 尝试打开应用程序
            print("\n===== 尝试打开微信 =====")
            success = SystemCommands.open_application(search_result['executable_path'])
            
            if success:
                print("微信启动成功，等待5秒后关闭...")
                time.sleep(5)
                
                # 关闭应用程序
                print("\n===== 关闭微信 =====")
                success = SystemCommands.close_application("微信")
                if success:
                    print("微信关闭成功")
                else:
                    print("微信关闭失败")
            else:
                print("微信启动失败")
        else:
            print("找不到可执行程序路径")
    else:
        print(f"找不到应用程序: {app_name}")
        
    # 测试通过名称映射直接打开应用程序
    print("\n===== 测试通过名称映射直接打开微信 =====")
    success = SystemCommands.open_application("微信")
    
    if success:
        print("微信启动成功，等待5秒后关闭...")
        time.sleep(5)
        
        # 关闭应用程序
        print("\n===== 关闭微信 =====")
        success = SystemCommands.close_application("微信")
        if success:
            print("微信关闭成功")
        else:
            print("微信关闭失败")
    else:
        print("微信启动失败")
    
    # 测试搜索不存在的应用程序
    print("\n===== 测试搜索不存在的应用程序 =====")
    app_name = "不存在的应用程序XYZABC"
    search_result = search_app(app_name)
    
    if search_result:
        print(f"意外找到了不存在的应用程序: {search_result['name']}")
    else:
        print(f"正确结果：找不到应用程序: {app_name}")
    
    # 测试搜索结果的匹配度
    print("\n===== 测试搜索结果的匹配度 =====")
    test_apps = ["微信", "记事本", "计算器", "画图", "浏览器"]
    
    for app in test_apps:
        search_result = search_app(app)
        if search_result:
            print(f"应用程序 '{app}' 匹配到 '{search_result['name']}', 匹配度: {search_result['match_score']}%")
        else:
            print(f"找不到应用程序: {app}")

def main():
    """主函数"""
    print("开始测试本地应用程序搜索功能...")
    
    # 测试本地应用程序搜索功能
    test_local_app_search()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main() 