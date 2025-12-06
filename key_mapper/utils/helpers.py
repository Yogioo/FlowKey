# -*- coding: utf-8 -*-
"""
工具函数
包含验证、格式化和常量定义
"""

import re
from typing import Optional, Dict, Any


def validate_key_string(key_str: str) -> bool:
    """验证按键字符串格式"""
    if not key_str or not isinstance(key_str, str):
        return False
    
    # 单个按键
    if len(key_str) == 1:
        return True
    
    # 组合键
    if '+' in key_str:
        parts = key_str.lower().split('+')
        valid_keys = {
            'ctrl', 'alt', 'shift', 'win', 'cmd', 'space', 'enter', 'tab',
            'backspace', 'delete', 'up', 'down', 'left', 'right',
            'home', 'end', 'page_up', 'page_down', 'esc',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
        }
        
        for part in parts:
            part = part.strip()
            if not part:
                return False
            if len(part) == 1:
                continue
            if part not in valid_keys:
                return False
        
        return True
    
    # 特殊按键
    special_keys = {
        'space', 'enter', 'tab', 'backspace', 'delete', 'up', 'down', 'left', 'right',
        'home', 'end', 'page_up', 'page_down', 'esc',
        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
    }
    
    return key_str.lower() in special_keys


def format_key_display(key_str: str) -> str:
    """格式化按键显示"""
    if not key_str:
        return ""
    
    # 转换为显示格式
    display_map = {
        'ctrl': 'Ctrl',
        'alt': 'Alt', 
        'shift': 'Shift',
        'win': 'Win',
        'cmd': 'Cmd',
        'space': 'Space',
        'enter': 'Enter',
        'tab': 'Tab',
        'backspace': 'Backspace',
        'delete': 'Delete',
        'up': '↑',
        'down': '↓',
        'left': '←',
        'right': '→',
        'home': 'Home',
        'end': 'End',
        'page_up': 'Page Up',
        'page_down': 'Page Down',
        'esc': 'Esc',
    }
    
    if '+' in key_str:
        parts = key_str.lower().split('+')
        formatted_parts = []
        for part in parts:
            part = part.strip()
            if part in display_map:
                formatted_parts.append(display_map[part])
            else:
                formatted_parts.append(part.upper())
        return ' + '.join(formatted_parts)
    else:
        lower_key = key_str.lower()
        return display_map.get(lower_key, key_str.upper())


def sanitize_key_string(key_str: str) -> str:
    """清理按键字符串"""
    if not key_str:
        return ""
    
    # 移除多余空格
    key_str = re.sub(r'\s+', '', key_str)
    
    # 转换为小写（除了单个字符）
    if len(key_str) > 1:
        key_str = key_str.lower()
    
    return key_str


def deep_merge_dict(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[Any, Any]:
    """深度合并字典"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result


def safe_get_nested(data: Dict[Any, Any], key_path: str, default: Any = None) -> Any:
    """安全获取嵌套字典值"""
    keys = key_path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def safe_set_nested(data: Dict[Any, Any], key_path: str, value: Any) -> None:
    """安全设置嵌套字典值"""
    keys = key_path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


# 常量定义
class Constants:
    """系统常量"""
    
    # 按键映射相关
    VALID_KEYS = {
        'ctrl', 'alt', 'shift', 'win', 'cmd', 'space', 'enter', 'tab',
        'backspace', 'delete', 'up', 'down', 'left', 'right',
        'home', 'end', 'page_up', 'page_down', 'esc',
        'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
    }
    
    # 模式相关
    DEFAULT_MODES = ["浏览模式", "影音模式", "视频模式", "窗口管理"]
    
    # 颜色主题
    THEME_COLORS = {
        "purple": ("#7c3aed", "#a855f7", "#4c1d95"),
        "blue": ("#3b82f6", "#60a5fa", "#1e40af"),
        "green": ("#10b981", "#34d399", "#064e3b"),
        "orange": ("#f59e0b", "#fbbf24", "#78350f"),
    }
    
    # 文件路径
    CONFIG_FILE = "key_mappings.json"
    APP_CONFIG_FILE = "wheel_tool_config.json"
    
    # 动画默认值
class ValidationError(Exception):
    """验证错误"""
    pass


class ConfigError(Exception):
    """配置错误"""
    pass