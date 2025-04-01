"""
提醒命令处理模块
处理提醒、倒计时等相关命令
"""

import logging
import re
from typing import Dict, Any
from src.utils.reminder import ReminderManager

logger = logging.getLogger(__name__)

def process_reminder_command(query: str) -> Dict[str, Any]:
    """
    处理提醒命令
    
    Args:
        query: 提醒命令字符串，如"3分钟后提醒我起床"
        
    Returns:
        Dict: 包含处理结果的字典
    """
    try:
        # 去除前后空格
        query = query.strip()
        
        logger.info(f"处理提醒命令: {query}")
        
        # 匹配时间模式：数字+单位+后，如"3分钟后"、"5小时后"、"10s后"
        time_pattern = r'(\d+)\s*(?:秒钟|秒|分钟|分|小时|小时|s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)后?'
        time_match = re.search(time_pattern, query, re.IGNORECASE)
        
        # 提取提醒内容
        content = query
        
        if time_match:
            # 提取时间字符串
            time_str = query[:time_match.end()]
            # 去掉末尾的"后"字
            if time_str.endswith("后"):
                time_str = time_str[:-1]
            
            # 提取提醒内容
            content = query[time_match.end():].strip()
            # 去除开头的"提醒我"等词语
            content_prefixes = ["提醒我", "提醒", "记得", "告诉我", "通知我"]
            for prefix in content_prefixes:
                if content.startswith(prefix):
                    content = content[len(prefix):].strip()
            
            # 如果内容为空，设置默认内容
            if not content:
                content = "时间到了"
            
            # 设置提醒
            logger.info(f"设置提醒: 时间={time_str}, 内容={content}")
            return ReminderManager.set_reminder(time_str, content)
        else:
            # 尝试提取"提醒我 时间 做某事"这种格式
            pattern = r'提醒我(?:在|过)?(?:\s*)(.+?)(?:时|分|点|秒钟|秒|分钟|分|小时|后)?(?:\s*)(.+)'
            match = re.search(pattern, query)
            
            if match:
                time_str = match.group(1).strip()
                content = match.group(2).strip()
                
                # 设置提醒
                logger.info(f"设置提醒: 时间={time_str}, 内容={content}")
                return ReminderManager.set_reminder(time_str, content)
            else:
                # 尝试提取纯数字 + 提醒内容的格式，如"10 提醒我起床"
                number_pattern = r'^(\d+)\s+(.+)'
                number_match = re.search(number_pattern, query)
                
                if number_match:
                    time_str = number_match.group(1).strip() + "秒"
                    content = number_match.group(2).strip()
                    
                    # 设置提醒
                    logger.info(f"设置提醒: 时间={time_str}, 内容={content}")
                    return ReminderManager.set_reminder(time_str, content)
                
                logger.warning(f"无法解析提醒命令: {query}")
                return {
                    "status": "error",
                    "message": "无法理解提醒格式，请尝试使用\"X分钟后提醒我...\"或\"提醒我在X分钟后...\"这样的格式"
                }
    
    except Exception as e:
        logger.error(f"处理提醒命令时出错: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"处理提醒命令时出错: {str(e)}"
        }

def process_countdown_command(query: str) -> Dict[str, Any]:
    """
    处理倒计时命令
    
    Args:
        query: 倒计时命令字符串，如"倒计时60秒"
        
    Returns:
        Dict: 包含处理结果的字典
    """
    try:
        # 去除前后空格
        query = query.strip()
        
        logger.info(f"处理倒计时命令: {query}")
        
        # 提取数字和单位
        time_pattern = r'(\d+)\s*(?:秒钟|秒|分钟|分|小时|s|sec|second|seconds|m|min|minute|minutes|h|hour|hours)?'
        match = re.search(time_pattern, query, re.IGNORECASE)
        
        # 提取倒计时内容
        content = "倒计时结束"
        content_pattern = r'(?:并)?(?:提醒|告诉|通知)(?:我)?(?:\s*)(.+)'
        content_match = re.search(content_pattern, query)
        
        if content_match:
            content = content_match.group(1).strip()
        
        if match:
            time_str = match.group(0).strip()
            
            # 如果只有数字没有单位，默认为秒
            if re.match(r'^\d+$', time_str):
                time_str = time_str + "秒"
            
            # 设置倒计时
            logger.info(f"设置倒计时: 时间={time_str}, 内容={content}")
            return ReminderManager.set_reminder(time_str, content, "倒计时")
        else:
            logger.warning(f"无法解析倒计时命令: {query}")
            return {
                "status": "error",
                "message": "无法理解倒计时格式，请尝试使用\"倒计时X秒\"或\"倒计时X分钟\"这样的格式"
            }
    
    except Exception as e:
        logger.error(f"处理倒计时命令时出错: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"处理倒计时命令时出错: {str(e)}"
        } 