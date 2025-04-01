import subprocess
import logging
import os
from typing import Optional, Dict, Any, List
import sys
import winreg
import json
import time

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
                return program
                
            # 检查环境变量PATH
            if os.name == 'nt':  # Windows系统
                # 添加.exe后缀（如果没有）
                if not program.endswith('.exe'):
                    program += '.exe'
                    
                # 在PATH中查找
                for path in os.environ["PATH"].split(os.pathsep):
                    exe_file = os.path.join(path, program)
                    if os.path.isfile(exe_file):
                        return exe_file
                        
                # 在注册表中查找
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\" + program)
                    path, _ = winreg.QueryValueEx(key, None)
                    if os.path.isfile(path):
                        return path
                except WindowsError:
                    pass
                    
            return None
            
        except Exception as e:
            logger.error(f"获取程序路径时出错: {e}")
            return None
    
    @staticmethod
    def _clean_app_name(app_name: str) -> str:
        """
        清理应用程序名称，移除标点符号和多余的空格
        
        Args:
            app_name: 原始应用程序名称
            
        Returns:
            str: 清理后的应用程序名称
        """
        # 移除常见的中文标点符号和空格
        punctuation = "。，、；：？！""''（）【】《》｛｝…～·"
        app_name = app_name.strip()
        for p in punctuation:
            app_name = app_name.replace(p, "")
        return app_name.strip()

    @staticmethod
    def open_application(app_name: str) -> bool:
        """
        打开指定的应用程序
        
        Args:
            app_name: 应用程序名称或完整路径
            
        Returns:
            bool: 是否成功打开应用程序
        """
        try:
            # 清理应用程序名称
            app_name = SystemCommands._clean_app_name(app_name)
            
            # Windows系统常用应用映射
            app_mapping = {
                "记事本": "notepad.exe",
                "计算器": "calc.exe",
                "画图": "mspaint.exe",
                "命令提示符": "cmd.exe",
                "资源管理器": "explorer.exe",
                "控制面板": "control.exe",
                "任务管理器": "taskmgr.exe",
                "系统设置": "ms-settings:",
                "写字板": "wordpad.exe",
                "媒体播放器": "wmplayer.exe",
                "注册表编辑器": "regedit.exe",
                "服务": "services.msc",
                "设备管理器": "devmgmt.msc",
                "磁盘管理": "diskmgmt.msc",
                "性能监视器": "perfmon.exe",
                "事件查看器": "eventvwr.msc",
                "组策略编辑器": "gpedit.msc",
                "远程桌面": "mstsc.exe",
                "powershell": "powershell.exe",
                "IE浏览器": "iexplore.exe",
                "声音设置": "mmsys.cpl",
                "防火墙设置": "firewall.cpl",
                "网络连接": "ncpa.cpl",
                "系统属性": "sysdm.cpl",
                "时间日期": "timedate.cpl",
                "显示设置": "desk.cpl",
                "鼠标设置": "main.cpl",
                "电源选项": "powercfg.cpl"
            }
            
            logger.info(f"尝试打开应用程序: {app_name}")
            
            # 获取实际的程序名
            actual_app = app_mapping.get(app_name, app_name)
            logger.debug(f"映射后的程序名: {actual_app}")
            
            success = False
            error_msg = None
            
            if os.name == 'nt':  # Windows系统
                # 获取程序完整路径
                program_path = SystemCommands._get_program_path(actual_app)
                if program_path:
                    logger.debug(f"找到程序路径: {program_path}")
                    try:
                        if program_path.endswith(('.msc', '.cpl')):
                            # 对于系统管理单元和控制面板项，使用特殊处理
                            subprocess.Popen(['mmc', program_path] if program_path.endswith('.msc') else ['control', program_path])
                            success = True
                        else:
                            # 使用startfile打开应用
                            os.startfile(program_path)
                            success = True
                    except Exception as e:
                        error_msg = str(e)
                else:
                    logger.debug(f"未找到程序路径，尝试直接执行: {actual_app}")
                    try:
                        # 如果找不到完整路径，尝试直接执行
                        process = subprocess.Popen(actual_app, shell=True)
                        # 等待一小段时间检查进程是否成功启动
                        time.sleep(0.1)
                        if process.poll() is None:  # 如果进程仍在运行
                            success = True
                        else:
                            error_msg = "进程启动后立即退出"
                    except Exception as e:
                        error_msg = str(e)
            else:
                # 对于其他操作系统，使用xdg-open
                try:
                    subprocess.Popen(['xdg-open', actual_app])
                    success = True
                except Exception as e:
                    error_msg = str(e)
                
            if success:
                logger.info(f"成功打开应用程序: {app_name}")
            else:
                logger.error(f"打开应用程序失败: {app_name}, 错误: {error_msg}")
                
            return success
            
        except Exception as e:
            logger.error(f"打开应用程序 {app_name} 失败: {e}")
            if os.name == 'nt':
                logger.debug(f"当前PATH环境变量: {os.environ.get('PATH', '')}")
            return False
    
    @staticmethod
    def close_application(app_name: str) -> bool:
        """
        关闭指定的应用程序
        
        Args:
            app_name: 应用程序名称
            
        Returns:
            bool: 是否成功关闭应用程序
        """
        try:
            # Windows系统常用应用映射（用于关闭）
            app_mapping = {
                "记事本": "notepad.exe",
                "计算器": "calc.exe",
                "画图": "mspaint.exe",
                "命令提示符": "cmd.exe",
                "资源管理器": "explorer.exe",
                "写字板": "wordpad.exe",
                "媒体播放器": "wmplayer.exe",
                "IE浏览器": "iexplore.exe",
                "任务管理器": "taskmgr.exe",
                "注册表编辑器": "regedit.exe",
                "powershell": "powershell.exe"
            }
            
            # 获取实际的程序名
            actual_app = app_mapping.get(app_name, app_name)
            logger.info(f"尝试关闭应用程序: {actual_app}")
            
            if os.name == 'nt':
                # Windows系统使用taskkill命令
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', actual_app], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    logger.info(f"成功关闭应用程序: {app_name}")
                    return True
                else:
                    logger.error(f"关闭应用程序失败，错误信息: {result.stderr}")
                    return False
            else:
                # Linux/Mac系统使用killall命令
                result = subprocess.run(
                    ['killall', actual_app], 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    logger.info(f"成功关闭应用程序: {app_name}")
                    return True
                else:
                    logger.error(f"关闭应用程序失败，错误信息: {result.stderr}")
                    return False
                
        except Exception as e:
            logger.error(f"关闭应用程序 {app_name} 失败: {e}")
            return False
    
    @staticmethod
    def handle_iot_command(command: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理物联网命令
        
        Args:
            command: 物联网命令字典
            
        Returns:
            Dict[str, Any]: 命令执行结果
        """
        try:
            logger.info(f"处理物联网命令: name={command.get('name')}, method={command.get('method')}, parameters={command.get('parameters')}")
            
            # 验证命令格式
            if not all(k in command for k in ['name', 'method', 'parameters']):
                return {
                    'success': False,
                    'message': '无效的命令格式',
                    'result': None
                }
                
            # 获取命令参数
            name = command['name']
            method = command['method']
            parameters = command['parameters']
            
            if name != "系统命令" or method != "Query":
                return {
                    'success': False,
                    'message': '不支持的命令类型',
                    'result': None
                }
                
            query = parameters.get('query', '').strip()
            if not query:
                return {
                    'success': False,
                    'message': '查询参数为空',
                    'result': None
                }
                
            # 解析命令
            if query.startswith('打开'):
                logger.info(f"正在打开应用程序: {query}")
                app_name = query[2:]  # 移除"打开"二字
                success = SystemCommands.open_application(app_name)
                
                result = {
                    'action': 'open',
                    'app_name': app_name,
                    'status': 'success' if success else 'failed'
                }
                
                return {
                    'success': success,
                    'message': f"打开{app_name}{'成功' if success else '失败'}",
                    'result': result
                }
                
            elif query.startswith('关闭'):
                logger.info(f"正在关闭应用程序: {query}")
                app_name = query[2:]  # 移除"关闭"二字
                success = SystemCommands.close_application(app_name)
                
                result = {
                    'action': 'close',
                    'app_name': app_name,
                    'status': 'success' if success else 'failed'
                }
                
                return {
                    'success': success,
                    'message': f"关闭{app_name}{'成功' if success else '失败'}",
                    'result': result
                }
            
            return {
                'success': False,
                'message': '不支持的操作',
                'result': None
            }
            
        except Exception as e:
            logger.error(f"处理物联网命令失败: {e}")
            return {
                'success': False,
                'message': f'命令执行出错: {str(e)}',
                'result': None
            }
    
    @staticmethod
    def handle_iot_commands(commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理多个物联网命令
        
        Args:
            commands: 物联网命令列表
            
        Returns:
            List[Dict]: 包含所有命令执行结果的列表
        """
        results = []
        for command in commands:
            result = SystemCommands.handle_iot_command(command)
            results.append(result)
        return results 