import os
import logging
import win32com.client
import difflib
import re
import winreg

logger = logging.getLogger(__name__)

def find_app_in_start_menu(app_name, min_score=60):
    """
    在Windows开始菜单中搜索应用程序快捷方式
    
    参数:
        app_name: 应用程序名称
        min_score: 最小匹配分数(0-100)，默认为60
        
    返回:
        dict: 包含快捷方式路径、可执行程序路径和匹配度的字典，如果找不到则返回None
    """
    try:
        logger.info(f"在开始菜单中搜索应用程序: {app_name}")
        
        # 开始菜单路径
        start_menu_paths = [
            os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
            os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
        ]
        
        # 用于存储找到的所有快捷方式
        all_shortcuts = []
        
        # 遍历开始菜单中的所有文件夹
        for start_menu_path in start_menu_paths:
            if os.path.exists(start_menu_path):
                for root, dirs, files in os.walk(start_menu_path):
                    for file in files:
                        if file.lower().endswith(".lnk"):
                            shortcut_path = os.path.join(root, file)
                            # 从快捷方式名称中移除.lnk后缀
                            shortcut_name = os.path.splitext(file)[0]
                            # 计算名称相似度
                            similarity = get_name_similarity(app_name, shortcut_name)
                            # 如果相似度高于阈值，则添加到列表中
                            if similarity >= min_score:
                                all_shortcuts.append({
                                    "shortcut_path": shortcut_path,
                                    "shortcut_name": shortcut_name,
                                    "similarity": similarity
                                })
        
        # 按相似度降序排序
        all_shortcuts.sort(key=lambda x: x["similarity"], reverse=True)
        
        # 如果找到了快捷方式，则获取可执行文件路径
        if all_shortcuts:
            best_match = all_shortcuts[0]
            shortcut_path = best_match["shortcut_path"]
            shortcut_name = best_match["shortcut_name"]
            similarity = best_match["similarity"]
            
            logger.info(f"找到最佳匹配: {shortcut_name} (路径: {shortcut_path}, 匹配度: {similarity}%)")
            
            # 获取快捷方式指向的可执行程序路径
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            target_path = shortcut.Targetpath
            
            logger.info(f"快捷方式指向的目标路径: {target_path}")
            
            return {
                "shortcut_path": shortcut_path,
                "shortcut_name": shortcut_name,
                "executable_path": target_path,
                "match_score": similarity
            }
        else:
            logger.warning(f"在开始菜单中找不到应用程序: {app_name}")
            return None
            
    except Exception as e:
        logger.error(f"搜索应用程序时出错: {str(e)}", exc_info=True)
        return None

def find_app_in_registry(app_name, min_score=70):
    """
    在Windows注册表中搜索已安装的应用程序
    
    参数:
        app_name: 应用程序名称
        min_score: 最小匹配分数(0-100)，默认为70
        
    返回:
        dict: 包含应用程序名称和路径的字典，如果找不到则返回None
    """
    try:
        logger.info(f"在注册表中搜索应用程序: {app_name}")
        
        # 注册表路径
        reg_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        # 用于存储找到的所有应用程序
        all_apps = []
        
        # 访问注册表
        for reg_path in reg_paths:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                for i in range(0, winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        
                        try:
                            # 获取应用程序名称
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            
                            # 尝试获取安装位置
                            try:
                                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            except:
                                install_location = ""
                                
                            # 计算名称相似度
                            similarity = get_name_similarity(app_name, display_name)
                            
                            # 如果相似度高于阈值，则添加到列表中
                            if similarity >= min_score:
                                all_apps.append({
                                    "name": display_name,
                                    "location": install_location,
                                    "similarity": similarity
                                })
                        except:
                            pass
                        finally:
                            winreg.CloseKey(subkey)
                    except:
                        continue
                winreg.CloseKey(key)
            except Exception as e:
                logger.error(f"访问注册表路径 {reg_path} 时出错: {str(e)}")
                continue
        
        # 按相似度降序排序
        all_apps.sort(key=lambda x: x["similarity"], reverse=True)
        
        # 返回最佳匹配
        if all_apps:
            best_match = all_apps[0]
            logger.info(f"在注册表中找到最佳匹配: {best_match['name']} (安装位置: {best_match['location']}, 匹配度: {best_match['similarity']}%)")
            return best_match
        else:
            logger.warning(f"在注册表中找不到应用程序: {app_name}")
            return None
            
    except Exception as e:
        logger.error(f"搜索应用程序时出错: {str(e)}", exc_info=True)
        return None

def get_name_similarity(name1, name2):
    """
    计算两个名称的相似度
    
    参数:
        name1: 第一个名称
        name2: 第二个名称
        
    返回:
        int: 相似度得分(0-100)
    """
    # 将名称转换为小写
    name1 = name1.lower()
    name2 = name2.lower()
    
    # 移除中文和英文名称中常见的后缀词
    suffixes = ["应用", "软件", "程序", "app", "软件", "客户端", "工具", "学习版", "专业版", 
                "免费版", "最新版", "官方版", "中文版", "英文版", "完整版", "精简版", "便携版"]
    
    for suffix in suffixes:
        name1 = name1.replace(suffix, "")
        name2 = name2.replace(suffix, "")
    
    # 精确匹配
    if name1 == name2:
        return 100
        
    # 名称包含关系
    if name1 in name2 or name2 in name1:
        # 计算较长字符串中较短字符串所占的比例
        longer = max(len(name1), len(name2))
        shorter = min(len(name1), len(name2))
        if longer > 0:  # 避免除以零
            return int(shorter / longer * 90)  # 最高90分
    
    # 使用difflib计算相似度
    similarity = difflib.SequenceMatcher(None, name1, name2).ratio()
    return int(similarity * 80)  # 最高80分
        
def search_app(app_name):
    """
    综合搜索应用程序，优先从开始菜单，然后从注册表
    
    参数:
        app_name: 应用程序名称
        
    返回:
        dict: 包含应用程序信息的字典，如果找不到则返回None
    """
    # 首先在开始菜单中搜索
    start_menu_result = find_app_in_start_menu(app_name)
    if start_menu_result:
        return {
            "name": start_menu_result["shortcut_name"],
            "executable_path": start_menu_result["executable_path"],
            "source": "start_menu",
            "match_score": start_menu_result["match_score"]
        }
    
    # 如果在开始菜单中找不到，则在注册表中搜索
    registry_result = find_app_in_registry(app_name)
    if registry_result:
        return {
            "name": registry_result["name"],
            "install_location": registry_result["location"],
            "source": "registry",
            "match_score": registry_result["similarity"]
        }
    
    # 如果都找不到，则返回None
    return None 