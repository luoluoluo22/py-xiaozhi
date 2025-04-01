import subprocess
import logging
import os
from typing import Optional, Dict, Any, List
import sys
import winreg
import json
import time
import win32com.client
from distutils.spawn import find_executable

logger = logging.getLogger(__name__)

class SystemCommands:
    """系统命令执行工具类"""
    
    @staticmethod
    def _get_program_path(program: str) -> Optional[str]:
        """
        获取程序的完整路径
        
        Args:
            program: 程序名称
            
        Returns:
            str: 程序的完整路径，如果找不到则返回None
        """
        try:
            # 首先检查是否是完整路径
            if os.path.isfile(program):
                logger.info(f"找到程序完整路径: {program}")
                return program
            
            logger.info(f"开始查找程序: {program}")
            
            # 创建不带扩展名的程序名，用于搜索.lnk文件
            program_name_no_ext = program
            if program.lower().endswith('.exe'):
                program_name_no_ext = program[:-4]
            
            # 第一步：搜索开始菜单中的快捷方式（最优先，因为能找到用户实际安装的程序）
            start_menu_paths = [
                os.path.join(os.environ.get("ProgramData", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
                os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu", "Programs"),
                # 添加桌面路径
                os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"),
                os.path.join(os.environ.get("PUBLIC", ""), "Desktop")
            ]
            
            # 尝试找到正确的快捷方式
            for start_menu_path in start_menu_paths:
                if os.path.exists(start_menu_path):
                    # 使用多级目录遍历寻找所有快捷方式
                    logger.debug(f"搜索目录: {start_menu_path}")
                    for root, dirs, files in os.walk(start_menu_path):
                        # 检查文件名是否匹配
                        name_matches = []
                        for file in files:
                            file_lower = file.lower()
                            if file_lower.endswith('.lnk'):
                                # 提取快捷方式名称（不含扩展名）
                                shortcut_name = os.path.splitext(file)[0].lower()
                                program_lower = program_name_no_ext.lower()
                                
                                # 检查完全匹配
                                if shortcut_name == program_lower:
                                    name_matches.append((file, 100))  # 完全匹配得分100
                                # 检查程序名是否包含在快捷方式名称中
                                elif program_lower in shortcut_name:
                                    name_matches.append((file, 80))  # 部分匹配得分80
                                # 检查快捷方式名称是否包含在程序名中
                                elif shortcut_name in program_lower:
                                    name_matches.append((file, 60))  # 反向包含得分60
                        
                        # 按匹配度排序
                        name_matches.sort(key=lambda x: x[1], reverse=True)
                        
                        # 处理找到的匹配项
                        for file, score in name_matches:
                            shortcut_path = os.path.join(root, file)
                            logger.info(f"找到可能的快捷方式: {shortcut_path}，匹配度: {score}")
                            
                            try:
                                # 解析快捷方式文件获取目标路径
                                shell = win32com.client.Dispatch("WScript.Shell")
                                shortcut = shell.CreateShortCut(shortcut_path)
                                target_path = shortcut.Targetpath
                                
                                # 额外检查目标路径是否包含程序名的关键部分（防止误匹配）
                                if os.path.isfile(target_path):
                                    target_filename = os.path.basename(target_path).lower()
                                    if (program_name_no_ext.lower() in target_filename or 
                                        target_filename in program_name_no_ext.lower() or
                                        score == 100):
                                        logger.info(f"快捷方式目标路径: {target_path}")
                                        return target_path
                                    else:
                                        logger.debug(f"快捷方式目标不匹配程序名: {target_path}")
                            except Exception as e:
                                logger.error(f"解析快捷方式失败: {e}")
                                continue
            
            # 第二步：按照不同类型的应用程序特别处理
            # 添加.exe后缀（如果没有）
            if not program.lower().endswith('.exe'):
                program_with_ext = f"{program}.exe"
            else:
                program_with_ext = program
                
            # 先在PATH中查找
            logger.debug("在PATH环境变量中查找程序")
            for path in os.environ.get("PATH", "").split(os.pathsep):
                exe_file = os.path.join(path, program_with_ext)
                if os.path.isfile(exe_file):
                    logger.info(f"在PATH中找到程序: {exe_file}")
                    return exe_file
            
            # 查询注册表中的App Paths
            try:
                logger.debug("在注册表App Paths中查找程序")
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\\" + program_with_ext)
                path, _ = winreg.QueryValueEx(key, None)
                if os.path.isfile(path):
                    logger.info(f"在注册表App Paths中找到程序: {path}")
                    return path
            except WindowsError:
                logger.debug(f"在注册表中未找到程序: {program_with_ext}")
            
            # 第三步：根据程序名特殊处理常见应用的路径
            # 微信
            if program.lower() in ["wechat", "wechat.exe", "微信"]:
                wechat_paths = [
                    r"C:\Program Files\Tencent\WeChat\WeChat.exe",
                    r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
                    os.path.join(os.environ.get("APPDATA", ""), "Tencent", "WeChat", "WeChat.exe")
                ]
                for wechat_path in wechat_paths:
                    if os.path.isfile(wechat_path):
                        logger.info(f"找到微信专用路径: {wechat_path}")
                        return wechat_path
            
            # QQ
            elif program.lower() in ["qq", "qq.exe"]:
                qq_paths = [
                    r"C:\Program Files\Tencent\QQ\Bin\QQ.exe",
                    r"C:\Program Files (x86)\Tencent\QQ\Bin\QQ.exe",
                    r"C:\Program Files\Tencent\QQNT\QQ.exe",  # 新版QQ路径
                    os.path.join(os.environ.get("APPDATA", ""), "Tencent", "QQ", "Bin", "QQ.exe")
                ]
                for qq_path in qq_paths:
                    if os.path.isfile(qq_path):
                        logger.info(f"找到QQ专用路径: {qq_path}")
                        return qq_path
            
            # 企业微信
            elif program.lower() in ["企业微信", "wxwork", "wxwork.exe"]:
                wxwork_paths = [
                    r"C:\Program Files\Tencent\WXWork\WXWork.exe",
                    r"C:\Program Files (x86)\Tencent\WXWork\WXWork.exe",
                    os.path.join(os.environ.get("APPDATA", ""), "Tencent", "WXWork", "WXWork.exe")
                ]
                for wxwork_path in wxwork_paths:
                    if os.path.isfile(wxwork_path):
                        logger.info(f"找到企业微信专用路径: {wxwork_path}")
                        return wxwork_path
            
            # 钉钉
            elif program.lower() in ["钉钉", "dingtalk", "dingtalk.exe"]:
                dingtalk_paths = [
                    r"C:\Program Files\DingTalk\DingtalkLauncher.exe",
                    r"C:\Program Files (x86)\DingTalk\DingtalkLauncher.exe",
                    os.path.join(os.environ.get("APPDATA", ""), "DingTalk", "DingtalkLauncher.exe")
                ]
                for dingtalk_path in dingtalk_paths:
                    if os.path.isfile(dingtalk_path):
                        logger.info(f"找到钉钉专用路径: {dingtalk_path}")
                        return dingtalk_path
            
            # 支付宝
            elif program.lower() in ["支付宝", "alipay", "alipay.exe"]:
                alipay_paths = [
                    r"C:\Program Files\Alipay\AliPaySecurity.exe",
                    r"C:\Program Files (x86)\Alipay\AliPaySecurity.exe",
                    os.path.join(os.environ.get("APPDATA", ""), "Alipay", "AliPaySecurity.exe")
                ]
                for alipay_path in alipay_paths:
                    if os.path.isfile(alipay_path):
                        logger.info(f"找到支付宝专用路径: {alipay_path}")
                        return alipay_path
            
            # Office应用
            elif program.lower() in ["word", "office word", "微软word"]:
                word_paths = [
                    r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
                    r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
                    r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
                    r"C:\Program Files (x86)\Microsoft Office\Office16\WINWORD.EXE"
                ]
                for word_path in word_paths:
                    if os.path.isfile(word_path):
                        logger.info(f"找到Word专用路径: {word_path}")
                        return word_path
            
            elif program.lower() in ["excel", "office excel", "微软excel"]:
                excel_paths = [
                    r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
                    r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
                    r"C:\Program Files\Microsoft Office\Office16\EXCEL.EXE",
                    r"C:\Program Files (x86)\Microsoft Office\Office16\EXCEL.EXE"
                ]
                for excel_path in excel_paths:
                    if os.path.isfile(excel_path):
                        logger.info(f"找到Excel专用路径: {excel_path}")
                        return excel_path
            
            elif program.lower() in ["powerpoint", "ppt", "office ppt"]:
                ppt_paths = [
                    r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
                    r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
                    r"C:\Program Files\Microsoft Office\Office16\POWERPNT.EXE",
                    r"C:\Program Files (x86)\Microsoft Office\Office16\POWERPNT.EXE"
                ]
                for ppt_path in ppt_paths:
                    if os.path.isfile(ppt_path):
                        logger.info(f"找到PowerPoint专用路径: {ppt_path}")
                        return ppt_path
            
            # 浏览器
            elif program.lower() in ["chrome", "谷歌浏览器", "google chrome"]:
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                ]
                for chrome_path in chrome_paths:
                    if os.path.isfile(chrome_path):
                        logger.info(f"找到Chrome专用路径: {chrome_path}")
                        return chrome_path
            
            elif program.lower() in ["firefox", "火狐浏览器", "firefox browser"]:
                firefox_paths = [
                    r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
                ]
                for firefox_path in firefox_paths:
                    if os.path.isfile(firefox_path):
                        logger.info(f"找到Firefox专用路径: {firefox_path}")
                        return firefox_path
            
            # 开发工具
            elif program.lower() in ["vscode", "vs code", "visual studio code"]:
                vscode_paths = [
                    r"C:\Program Files\Microsoft VS Code\Code.exe",
                    r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
                    r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe".replace("{username}", os.environ.get("USERNAME", ""))
                ]
                for vscode_path in vscode_paths:
                    if os.path.isfile(vscode_path):
                        logger.info(f"找到VS Code专用路径: {vscode_path}")
                        return vscode_path
            
            # 第四步：在常见程序目录中搜索（这步可能较慢，因此放在最后）
            common_dirs = [
                os.path.join(os.environ.get("ProgramFiles", "")),
                os.path.join(os.environ.get("ProgramFiles(x86)", "")),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
                os.path.join(os.environ.get("APPDATA", ""))
            ]
            
            logger.debug("在常见安装目录中搜索程序")
            # 为了防止搜索时间过长，限制搜索深度
            max_depth = 3
            for common_dir in common_dirs:
                if os.path.exists(common_dir):
                    for root, dirs, files in os.walk(common_dir):
                        # 计算当前深度
                        current_depth = root[len(common_dir):].count(os.sep)
                        if current_depth > max_depth:
                            dirs[:] = []  # 清空dirs列表以停止更深层次的搜索
                            continue
                            
                        # 检查文件是否匹配
                        for file in files:
                            file_lower = file.lower()
                            if file_lower == program_with_ext.lower():
                                found_path = os.path.join(root, file)
                                logger.info(f"在目录搜索中找到程序: {found_path}")
                                return found_path
                            
                            # 额外检查程序名是否是文件名的一部分
                            prog_part = program_name_no_ext.lower()
                            if prog_part in file_lower and file_lower.endswith('.exe'):
                                found_path = os.path.join(root, file)
                                logger.info(f"在目录搜索中找到可能匹配的程序: {found_path}")
                                return found_path
                                
            logger.error(f"无法找到程序路径: {program}")
            return None
            
        except Exception as e:
            logger.error(f"获取程序路径时出错: {str(e)}", exc_info=True)
            return None
    
    @staticmethod
    def _clean_app_name(app_name: str) -> str:
        """
        清理应用程序名称，移除常见前缀和后缀
        
        参数:
            app_name: 原始应用程序名称
            
        返回:
            str: 清理后的应用程序名称
        """
        # 移除常见前缀
        prefixes = ["打开", "启动", "运行", "执行", "开启", "start", "open", "run", "execute"]
        for prefix in prefixes:
            if app_name.lower().startswith(prefix.lower()):
                app_name = app_name[len(prefix):].strip()
                break
                
        # 移除常见后缀
        suffixes = ["程序", "软件", "应用", "app", "application", "program"]
        for suffix in suffixes:
            if app_name.lower().endswith(suffix.lower()):
                app_name = app_name[:-len(suffix)].strip()
                break
                
        return app_name

    @staticmethod
    def open_application(app_name: str):
        """
        打开指定的应用程序
        
        参数:
            app_name: 应用程序名称或完整路径
            
        返回:
            bool: 操作是否成功
        """
        # 清理应用名称
        app_name = SystemCommands._clean_app_name(app_name)
        
        # 应用程序映射表
        app_mapping = {
            # 系统工具
            "记事本": "notepad.exe",
            "笔记本": "notepad.exe",
            "notepad": "notepad.exe",
            
            "计算器": "calc.exe",
            "calculator": "calc.exe",
            
            "画图": "mspaint.exe",
            "绘图": "mspaint.exe",
            "画板": "mspaint.exe",
            "paint": "mspaint.exe",
            "mspaint": "mspaint.exe",
            
            "浏览器": "msedge.exe",
            "edge浏览器": "msedge.exe",
            "edge": "msedge.exe",
            "微软浏览器": "msedge.exe",
            "microsoft edge": "msedge.exe",
            
            "资源管理器": "explorer.exe",
            "文件资源管理器": "explorer.exe",
            "我的电脑": "explorer.exe",
            "文件夹": "explorer.exe",
            "explorer": "explorer.exe",
            
            "任务管理器": "taskmgr.exe",
            "进程管理器": "taskmgr.exe",
            "task manager": "taskmgr.exe",
            
            "控制面板": "control.exe",
            "control panel": "control.exe",
            
            "cmd": "cmd.exe",
            "命令提示符": "cmd.exe",
            "命令行": "cmd.exe",
            "command prompt": "cmd.exe",
            
            "powershell": "powershell.exe",
            "power shell": "powershell.exe",
            "微软powershell": "powershell.exe",
            
            "终端": "wt.exe",
            "windows terminal": "wt.exe",
            "terminal": "wt.exe",
            
            "设置": "ms-settings:",
            "系统设置": "ms-settings:",
            "windows设置": "ms-settings:",
            "settings": "ms-settings:",
            
            # 系统管理工具
            "系统信息": "msinfo32.exe",
            "system info": "msinfo32.exe",
            
            "注册表编辑器": "regedit.exe",
            "注册表": "regedit.exe",
            "registry editor": "regedit.exe",
            
            "磁盘清理": "cleanmgr.exe",
            "disk cleanup": "cleanmgr.exe",
            
            "字符映射表": "charmap.exe",
            "character map": "charmap.exe",
            
            "性能监视器": "perfmon.exe",
            "performance monitor": "perfmon.exe",
            
            # MSC文件
            "服务": "services.msc",
            "服务管理": "services.msc",
            "services": "services.msc",
            
            "设备管理器": "devmgmt.msc",
            "device manager": "devmgmt.msc",
            
            "计算机管理": "compmgmt.msc",
            "computer management": "compmgmt.msc",
            
            "事件查看器": "eventvwr.msc",
            "event viewer": "eventvwr.msc",
            
            "磁盘管理": "diskmgmt.msc",
            "磁盘管理器": "diskmgmt.msc",
            "disk management": "diskmgmt.msc",
            
            "组策略": "gpedit.msc",
            "组策略编辑器": "gpedit.msc",
            "group policy": "gpedit.msc",
            
            "本地安全策略": "secpol.msc",
            "安全策略": "secpol.msc",
            "security policy": "secpol.msc",
            
            # 其他系统应用
            "远程桌面": "mstsc.exe",
            "远程连接": "mstsc.exe",
            "remote desktop": "mstsc.exe",
            
            "系统版本": "winver.exe",
            "windows版本": "winver.exe",
            "版本信息": "winver.exe",
            "winver": "winver.exe",
            "windows version": "winver.exe",
            
            # CPL文件
            "声音设置": "mmsys.cpl",
            "音频设置": "mmsys.cpl",
            "声音": "mmsys.cpl",
            "sound settings": "mmsys.cpl",
            
            "网络连接": "ncpa.cpl",
            "网络设置": "ncpa.cpl",
            "network connections": "ncpa.cpl",
            
            "电源选项": "powercfg.cpl",
            "电源设置": "powercfg.cpl",
            "power options": "powercfg.cpl",
            
            "鼠标设置": "main.cpl",
            "鼠标": "main.cpl",
            "mouse settings": "main.cpl",
            
            "区域设置": "intl.cpl",
            "地区设置": "intl.cpl",
            "regional settings": "intl.cpl",
            
            "显示设置": "desk.cpl",
            "屏幕设置": "desk.cpl",
            "显示器设置": "desk.cpl",
            "display settings": "desk.cpl",
            
            "日期和时间": "timedate.cpl",
            "时间设置": "timedate.cpl",
            "日期时间": "timedate.cpl",
            "date and time": "timedate.cpl",
            
            "防火墙设置": "firewall.cpl",
            "防火墙": "firewall.cpl",
            "firewall": "firewall.cpl",
            
            "添加删除程序": "appwiz.cpl",
            "程序和功能": "appwiz.cpl",
            "卸载程序": "appwiz.cpl",
            "programs and features": "appwiz.cpl",
            
            # 常用应用 - 使用特殊查找逻辑
            "微信": "微信",
            "wechat": "微信",
            
            "qq": "QQ",
            "腾讯qq": "QQ",
            "qq聊天": "QQ",
            
            "钉钉": "钉钉",
            "dingtalk": "钉钉",
            "阿里钉钉": "钉钉",
            
            "腾讯会议": "腾讯会议",
            "tencent meeting": "腾讯会议",
            "会议": "腾讯会议",
            
            "支付宝": "支付宝",
            "alipay": "支付宝",
            "蚂蚁支付宝": "支付宝",
            
            "网易云音乐": "网易云音乐",
            "网易云": "网易云音乐",
            "cloud music": "网易云音乐",
            "音乐播放器": "网易云音乐",
            
            # Office应用 - 使用特殊查找逻辑
            "office": "Office",
            "微软office": "Office",
            "ms office": "Office",
            
            "word": "Word",
            "微软word": "Word",
            "文档": "Word",
            "办公word": "Word",
            
            "excel": "Excel",
            "微软excel": "Excel",
            "表格": "Excel",
            "办公excel": "Excel",
            
            "powerpoint": "PowerPoint",
            "ppt": "PowerPoint",
            "演示文稿": "PowerPoint",
            "幻灯片": "PowerPoint",
            "微软ppt": "PowerPoint",
            "办公ppt": "PowerPoint",
            
            # 开发工具 - 使用特殊查找逻辑
            "visual studio": "Visual Studio",
            "vs": "Visual Studio",
            "visualstudio": "Visual Studio",
            
            "vscode": "VS Code",
            "vs code": "VS Code",
            "visual studio code": "VS Code",
            "代码编辑器": "VS Code",
            
            # 浏览器 - 使用特殊查找逻辑
            "chrome": "Chrome",
            "谷歌浏览器": "Chrome",
            "google chrome": "Chrome",
            "谷歌": "Chrome",
            
            "火狐浏览器": "Firefox",
            "firefox": "Firefox",
            "火狐": "Firefox",
            "mozilla firefox": "Firefox",
            
            # 企业办公 - 使用特殊查找逻辑
            "企业微信": "企业微信",
            "企微": "企业微信",
            "wxwork": "企业微信",
            
            "飞书": "飞书",
            "字节飞书": "飞书",
            "lark": "飞书",
            "feishu": "飞书"
        }
        
        logger.info(f"尝试打开应用程序: {app_name}")
        
        # 如果在映射表中找到对应的程序名
        if app_name.lower() in map(str.lower, app_mapping.keys()):
            # 获取映射的程序名（区分大小写）
            mapped_name = None
            for key in app_mapping.keys():
                if key.lower() == app_name.lower():
                    mapped_name = app_mapping[key]
                    break
                    
            if mapped_name:
                logger.info(f"应用程序 '{app_name}' 已映射到 '{mapped_name}'")
                app_name = mapped_name
        
        # 特殊处理常用应用程序（需要搜索本地系统）
        special_apps = {
            "微信": ["微信", "WeChat"],
            "wechat": ["微信", "WeChat"],
            "qq": ["QQ", "TencentQQ"],
            "腾讯qq": ["QQ", "TencentQQ"],
            "钉钉": ["钉钉", "DingTalk"],
            "dingtalk": ["钉钉", "DingTalk"],
            "企业微信": ["企业微信", "WXWork"],
            "企微": ["企业微信", "WXWork"],
            "wxwork": ["企业微信", "WXWork"],
            "chrome": ["Google Chrome", "谷歌浏览器"],
            "谷歌浏览器": ["Google Chrome", "谷歌浏览器"],
            "谷歌": ["Google Chrome", "谷歌浏览器"],
            "火狐": ["Firefox", "火狐浏览器"],
            "firefox": ["Firefox", "火狐浏览器"],
            "word": ["Word", "Microsoft Word"],
            "微软word": ["Word", "Microsoft Word"],
            "excel": ["Excel", "Microsoft Excel"],
            "微软excel": ["Excel", "Microsoft Excel"],
            "powerpoint": ["PowerPoint", "Microsoft PowerPoint"],
            "ppt": ["PowerPoint", "Microsoft PowerPoint"]
        }
        
        app_lower = app_name.lower()
        if app_lower in special_apps:
            search_terms = special_apps[app_lower]
            
            # 使用开始菜单搜索应用程序
            from src.utils.app_finder import search_app
            for term in search_terms:
                search_result = search_app(term)
                if search_result and 'executable_path' in search_result:
                    app_name = search_result['executable_path']
                    logger.info(f"特殊处理应用路径 '{term}': {app_name}")
                    break
        
        # 检查是否是完整路径
        if os.path.exists(app_name) and os.access(app_name, os.X_OK):
            program_path = app_name
            logger.info(f"使用完整路径: {program_path}")
        else:
            # 检查是否是特殊文件类型
            if app_name.endswith('.msc'):
                program_path = app_name
                logger.info(f"检测到MSC文件: {program_path}")
            elif app_name.endswith('.cpl'):
                program_path = app_name
                logger.info(f"检测到CPL文件: {program_path}")
            elif app_name.startswith('ms-settings:'):
                program_path = app_name
                logger.info(f"检测到设置URI: {program_path}")
            else:
                # 尝试在系统路径中查找可执行文件
                program_path = find_executable(app_name)
                
                # 如果找不到，则尝试在开始菜单中搜索快捷方式
                if not program_path and os.name == 'nt':  # 仅在Windows系统下执行
                    from src.utils.app_finder import find_app_in_start_menu
                    search_result = find_app_in_start_menu(app_name)
                    
                    if search_result and search_result['executable_path']:
                        program_path = search_result['executable_path']
                        logger.info(f"在开始菜单中找到应用程序: {program_path} (匹配度: {search_result['match_score']}%)")
        
        # 如果找到了程序路径，则尝试打开
        if program_path:
            try:
                logger.info(f"尝试启动程序: {program_path}")
                
                # 根据文件类型选择不同的启动方式
                if program_path.endswith('.msc'):
                    cmd = f'mmc {program_path}'
                    subprocess.Popen(cmd, shell=True)
                elif program_path.endswith('.cpl'):
                    cmd = f'control {program_path}'
                    subprocess.Popen(cmd, shell=True)
                elif program_path.startswith('ms-settings:'):
                    cmd = f'start {program_path}'
                    subprocess.Popen(cmd, shell=True)
                else:
                    # 根据操作系统选择不同的启动方式
                    if os.name == 'nt':  # Windows
                        subprocess.Popen(f'start "" "{program_path}"', shell=True)
                    else:  # Linux/Mac
                        subprocess.Popen([program_path])
                
                logger.info(f"已成功启动应用程序: {app_name}")
                return True
            except Exception as e:
                logger.error(f"启动应用程序失败: {app_name}, 错误: {str(e)}", exc_info=True)
                return False
        else:
            logger.error(f"无法找到应用程序路径: {app_name}")
            return False
            
    @staticmethod
    def close_application(app_name: str):
        """
        关闭指定的应用程序
        
        参数:
            app_name: 应用程序名称或进程名
            
        返回:
            bool: 操作是否成功
        """
        # 清理应用名称
        app_name = SystemCommands._clean_app_name(app_name)
        
        # 应用程序映射表（与open_application中相同）
        app_mapping = {
            # 系统工具
            "记事本": "notepad.exe",
            "笔记本": "notepad.exe",
            "notepad": "notepad.exe",
            
            # 其他映射（省略重复代码）...
            # 实际使用时请复制open_application中的完整映射表
        }
        
        logger.info(f"尝试关闭应用程序: {app_name}")
        
        # 如果在映射表中找到对应的程序名
        if app_name.lower() in map(str.lower, app_mapping.keys()):
            # 获取映射的程序名（区分大小写）
            mapped_name = None
            for key in app_mapping.keys():
                if key.lower() == app_name.lower():
                    mapped_name = app_mapping[key]
                    break
                    
            if mapped_name:
                logger.info(f"应用程序 '{app_name}' 已映射到 '{mapped_name}'")
                app_name = mapped_name
        
        # 特殊处理常用应用程序
        special_app_processes = {
            "微信": "WeChat.exe",
            "wechat": "WeChat.exe",
            "qq": "QQ.exe",
            "腾讯qq": "QQ.exe",
            "钉钉": "DingTalk.exe",
            "dingtalk": "DingTalk.exe",
            "企业微信": "WXWork.exe",
            "企微": "WXWork.exe",
            "wxwork": "WXWork.exe",
            "chrome": "chrome.exe",
            "谷歌浏览器": "chrome.exe",
            "google chrome": "chrome.exe",
            "谷歌": "chrome.exe",
            "火狐": "firefox.exe",
            "firefox": "firefox.exe",
            "火狐浏览器": "firefox.exe",
            "word": "WINWORD.EXE",
            "微软word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "微软excel": "EXCEL.EXE",
            "powerpoint": "POWERPNT.EXE",
            "ppt": "POWERPNT.EXE",
            "微软ppt": "POWERPNT.EXE",
            "计算器": "CalculatorApp.exe",
            "calculator": "CalculatorApp.exe"
        }
        
        app_lower = app_name.lower()
        if app_lower in special_app_processes:
            process_name = special_app_processes[app_lower]
            logger.info(f"特殊处理应用进程名: {process_name}")
            app_name = process_name
        
        # 如果程序名不包含扩展名，尝试添加.exe扩展名（仅在Windows下）
        if os.name == 'nt' and not '.' in app_name:
            app_name = f"{app_name}.exe"
            
        try:
            if os.name == 'nt':  # Windows
                # 使用taskkill命令关闭进程
                logger.info(f"执行taskkill命令: taskkill /F /IM {app_name}")
                process = subprocess.run(f"taskkill /F /IM {app_name}", 
                                         shell=True, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
                
                # 检查命令执行结果
                if process.returncode == 0:
                    logger.info(f"成功关闭应用程序: {app_name}")
                    return True
                else:
                    error_msg = process.stderr.decode('utf-8', errors='ignore')
                    if "没有运行的任务" in error_msg or "not found" in error_msg:
                        logger.warning(f"应用程序未运行: {app_name}")
                        return True  # 如果程序不在运行，也视为成功
                    else:
                        logger.error(f"关闭应用程序失败: {app_name}, 错误: {error_msg}")
                        return False
            else:  # Linux/Mac
                # 使用pkill命令关闭进程
                logger.info(f"执行pkill命令: pkill -f {app_name}")
                process = subprocess.run(f"pkill -f {app_name}", 
                                         shell=True, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
                
                # 检查命令执行结果
                if process.returncode <= 1:  # 0=成功, 1=没有匹配的进程
                    logger.info(f"成功关闭应用程序: {app_name}")
                    return True
                else:
                    error_msg = process.stderr.decode('utf-8', errors='ignore')
                    logger.error(f"关闭应用程序失败: {app_name}, 错误: {error_msg}")
                    return False
                    
        except Exception as e:
            logger.error(f"关闭应用程序时出错: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def handle_iot_command(command: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理IoT格式的命令
        
        参数:
            command: IoT命令字典，格式如下：
                {
                    "name": "系统命令",
                    "method": "Query",
                    "parameters": {
                        "query": "打开记事本"
                    }
                }
            
        返回:
            Dict: 包含执行结果的字典
        """
        try:
            # 日志记录接收到的命令
            logger.info(f"处理IoT命令: {json.dumps(command, ensure_ascii=False)}")
            
            # 验证命令格式
            if not isinstance(command, dict):
                logger.error(f"命令格式错误，应为字典: {command}")
                return {
                    "status": "error",
                    "message": "命令格式错误，应为字典"
                }
                
            if "name" not in command:
                logger.error(f"命令缺少name字段: {command}")
                return {
                    "status": "error",
                    "message": "命令缺少name字段"
                }
                
            if "method" not in command:
                logger.error(f"命令缺少method字段: {command}")
                return {
                    "status": "error",
                    "message": "命令缺少method字段"
                }
                
            if "parameters" not in command:
                logger.error(f"命令缺少parameters字段: {command}")
                return {
                    "status": "error",
                    "message": "命令缺少parameters字段"
                }
            
            # 解析命令
            name = command["name"]
            method = command["method"]
            parameters = command["parameters"]
            
            # 仅处理系统命令
            if name != "系统命令":
                logger.warning(f"未知命令类型: {name}")
                return {
                    "status": "error",
                    "message": f"未知命令类型: {name}"
                }
            
            # 处理Query方法
            if method == "Query":
                if "query" not in parameters:
                    logger.error(f"Query方法缺少query参数: {parameters}")
                    return {
                        "status": "error",
                        "message": "Query方法缺少query参数"
                    }
                
                query = parameters["query"]
                logger.info(f"处理查询命令: {query}")
                
                # 判断是打开还是关闭应用
                if "打开" in query or "启动" in query or "运行" in query or "开启" in query:
                    # 提取应用名称
                    app_prefixes = ["打开", "启动", "运行", "开启"]
                    app_name = query
                    for prefix in app_prefixes:
                        if query.startswith(prefix):
                            app_name = query[len(prefix):].strip()
                            break
                    
                    logger.info(f"从查询中提取应用名称: {app_name}")
                    
                    # 执行打开应用操作
                    success = SystemCommands.open_application(app_name)
                    
                    # 返回执行结果
                    if success:
                        logger.info(f"成功打开应用: {app_name}")
                        return {
                            "status": "success",
                            "message": f"已打开{app_name}",
                            "action": "open",
                            "app_name": app_name,
                            "success": True
                        }
                    else:
                        logger.error(f"打开应用失败: {app_name}")
                        return {
                            "status": "error",
                            "message": f"无法打开{app_name}",
                            "action": "open",
                            "app_name": app_name,
                            "success": False
                        }
                        
                elif "关闭" in query or "停止" in query or "退出" in query or "结束" in query:
                    # 提取应用名称
                    app_prefixes = ["关闭", "停止", "退出", "结束"]
                    app_name = query
                    for prefix in app_prefixes:
                        if query.startswith(prefix):
                            app_name = query[len(prefix):].strip()
                            break
                    
                    logger.info(f"从查询中提取应用名称: {app_name}")
                    
                    # 执行关闭应用操作
                    success = SystemCommands.close_application(app_name)
                    
                    # 返回执行结果
                    if success:
                        logger.info(f"成功关闭应用: {app_name}")
                        return {
                            "status": "success",
                            "message": f"已关闭{app_name}",
                            "action": "close",
                            "app_name": app_name,
                            "success": True
                        }
                    else:
                        logger.error(f"关闭应用失败: {app_name}")
                        return {
                            "status": "error",
                            "message": f"无法关闭{app_name}",
                            "action": "close",
                            "app_name": app_name,
                            "success": False
                        }
                else:
                    logger.warning(f"未识别的查询命令: {query}")
                    return {
                        "status": "error",
                        "message": f"未识别的查询命令: {query}"
                    }
            else:
                logger.warning(f"不支持的方法: {method}")
                return {
                    "status": "error",
                    "message": f"不支持的方法: {method}"
                }
                
        except Exception as e:
            logger.error(f"处理IoT命令时出错: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"处理命令时出错: {str(e)}"
            }
    
    @staticmethod
    def handle_iot_commands(commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量处理IoT格式的命令
        
        参数:
            commands: IoT命令字典列表
            
        返回:
            List[Dict]: 包含每个命令执行结果的列表
        """
        results = []
        
        for command in commands:
            try:
                result = SystemCommands.handle_iot_command(command)
                results.append(result)
            except Exception as e:
                logger.error(f"处理命令时出错: {str(e)}", exc_info=True)
                results.append({
                    "status": "error",
                    "message": f"处理命令时出错: {str(e)}"
                })
        
        return results 