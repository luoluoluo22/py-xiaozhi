import os
import sys
import subprocess
import logging
import winreg
import glob
import win32com.client

# 添加src目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def get_installed_apps_from_registry():
    """从注册表获取已安装的应用程序"""
    app_list = []
    
    # 遍历64位应用
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        count = winreg.QueryInfoKey(key)[0]
        
        for i in range(count):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                
                try:
                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    app_list.append({
                        "name": name,
                        "source": "registry_64bit",
                        "registry_key": subkey_name
                    })
                except (WindowsError, FileNotFoundError):
                    pass
                    
                winreg.CloseKey(subkey)
            except (WindowsError, FileNotFoundError):
                continue
                
        winreg.CloseKey(key)
    except (WindowsError, FileNotFoundError):
        logger.error("无法访问64位卸载注册表")
    
    # 遍历32位应用
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
        count = winreg.QueryInfoKey(key)[0]
        
        for i in range(count):
            try:
                subkey_name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, subkey_name)
                
                try:
                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                    app_list.append({
                        "name": name,
                        "source": "registry_32bit",
                        "registry_key": subkey_name
                    })
                except (WindowsError, FileNotFoundError):
                    pass
                    
                winreg.CloseKey(subkey)
            except (WindowsError, FileNotFoundError):
                continue
                
        winreg.CloseKey(key)
    except (WindowsError, FileNotFoundError):
        logger.error("无法访问32位卸载注册表")
    
    return app_list

def get_start_menu_shortcuts():
    """获取开始菜单中的快捷方式"""
    shortcut_list = []
    
    # 开始菜单路径
    start_menu_paths = [
        os.path.join(os.environ.get("ProgramData", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs")
    ]
    
    for start_menu_path in start_menu_paths:
        if os.path.exists(start_menu_path):
            # 遍历快捷方式
            for root, dirs, files in os.walk(start_menu_path):
                for file in files:
                    if file.lower().endswith(".lnk"):
                        shortcut_path = os.path.join(root, file)
                        
                        try:
                            # 解析快捷方式
                            shell = win32com.client.Dispatch("WScript.Shell")
                            shortcut = shell.CreateShortCut(shortcut_path)
                            target_path = shortcut.Targetpath
                            
                            # 获取名称（不含扩展名）
                            name = os.path.splitext(file)[0]
                            
                            # 获取相对路径（从开始菜单根目录开始）
                            rel_path = os.path.relpath(shortcut_path, start_menu_path)
                            folder = os.path.dirname(rel_path)
                            
                            shortcut_list.append({
                                "name": name,
                                "shortcut_path": shortcut_path,
                                "target_path": target_path,
                                "folder": folder,
                                "source": "start_menu"
                            })
                        except Exception as e:
                            logger.error(f"解析快捷方式失败: {shortcut_path}, 错误: {e}")
    
    return shortcut_list

def get_common_apps_by_paths():
    """检查常见应用程序路径"""
    common_paths = {
        "WeChat": [
            r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
        ],
        "QQ": [
            r"C:\Program Files\Tencent\QQ\Bin\QQ.exe",
            r"C:\Program Files (x86)\Tencent\QQ\Bin\QQ.exe",
            r"C:\Program Files\Tencent\QQNT\QQ.exe"
        ],
        "WXWork": [
            r"C:\Program Files\Tencent\WXWork\WXWork.exe",
            r"C:\Program Files (x86)\Tencent\WXWork\WXWork.exe"
        ],
        "DingTalk": [
            r"C:\Program Files\DingTalk\DingtalkLauncher.exe",
            r"C:\Program Files (x86)\DingTalk\DingtalkLauncher.exe"
        ],
        "Chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ],
        "Firefox": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        ],
        "Microsoft Office": [
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE"
        ]
    }
    
    found_apps = []
    
    for app_name, paths in common_paths.items():
        for path in paths:
            if os.path.isfile(path):
                found_apps.append({
                    "name": app_name,
                    "path": path,
                    "source": "common_path"
                })
                break
    
    return found_apps

def list_running_processes():
    """列出当前运行的进程"""
    try:
        # 使用tasklist命令获取运行中的进程
        result = subprocess.run(['tasklist', '/FO', 'CSV'], capture_output=True, text=True, check=True)
        
        processes = []
        for line in result.stdout.strip().split('\n')[1:]:  # 跳过标题行
            try:
                parts = line.strip('"').split('","')
                if len(parts) >= 2:
                    process_name = parts[0]
                    pid = parts[1]
                    processes.append({
                        "name": process_name,
                        "pid": pid,
                        "source": "running_process"
                    })
            except Exception as e:
                logger.error(f"解析进程信息失败: {line}, 错误: {e}")
        
        return processes
    except Exception as e:
        logger.error(f"获取运行进程列表失败: {e}")
        return []

def print_app_list(apps, title):
    """打印应用程序列表"""
    print(f"\n===== {title} =====")
    
    # 排序
    sorted_apps = sorted(apps, key=lambda x: x.get("name", "").lower())
    
    # 打印
    for i, app in enumerate(sorted_apps, 1):
        name = app.get("name", "未知")
        source = app.get("source", "未知")
        
        if source == "registry_64bit" or source == "registry_32bit":
            print(f"{i}. {name} (来源: {source})")
        elif source == "start_menu":
            target = app.get("target_path", "")
            folder = app.get("folder", "")
            print(f"{i}. {name} (来源: 开始菜单/{folder}, 目标: {target})")
        elif source == "common_path":
            path = app.get("path", "")
            print(f"{i}. {name} (来源: 常见路径, 路径: {path})")
        elif source == "running_process":
            pid = app.get("pid", "")
            print(f"{i}. {name} (PID: {pid})")
        else:
            print(f"{i}. {name}")
    
    print(f"总计: {len(sorted_apps)} 个应用")

def main():
    """主函数"""
    print("开始检索已安装的应用程序...")
    
    # 从注册表获取已安装应用
    registry_apps = get_installed_apps_from_registry()
    print_app_list(registry_apps, "从注册表检索到的应用程序")
    
    # 获取开始菜单快捷方式
    shortcuts = get_start_menu_shortcuts()
    print_app_list(shortcuts, "开始菜单中的应用程序快捷方式")
    
    # 检查常见应用路径
    common_apps = get_common_apps_by_paths()
    print_app_list(common_apps, "常见应用程序检查")
    
    # 列出运行中的进程
    processes = list_running_processes()
    print_app_list(processes, "当前运行的进程")
    
    print("\n检索完成！")

if __name__ == "__main__":
    main() 