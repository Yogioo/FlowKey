# -*- coding: utf-8 -*-
"""
数据模型类
包含按键映射和模式相关的核心数据结构
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Callable
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
from .executors import ActionExecutor


class KeyMapping:
    """单个按键映射"""

    def __init__(self, source_key: str, target_key: str, block: bool = True, hint: str = "", action_type: str = "keyboard"):
        self.source_key = source_key  # 源按键
        self.target_key = target_key  # 目标按键
        self.block = block  # 是否屏蔽源按键，默认True
        self.hint = hint  # 触发提示文本
        self.action_type = action_type  # 动作类型：keyboard, mouse_scroll, mouse_click, command

    def to_dict(self) -> dict:
        result = {
            "source": self.source_key,
            "target": self.target_key,
            "block": self.block,
            "action_type": self.action_type
        }
        if self.hint:
            result["hint"] = self.hint
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "KeyMapping":
        return cls(
            data["source"],
            data["target"],
            data.get("block", True),
            data.get("hint", ""),
            data.get("action_type", "keyboard")  # 向后兼容：默认为 keyboard
        )


class ModeConfig:
    """模式配置数据类"""
    
    def __init__(self, enabled: bool = True, mappings: Optional[Dict[str, KeyMapping]] = None):
        self.enabled = enabled
        self.mappings = mappings or {}

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "mappings": [m.to_dict() for m in self.mappings.values()]
        }

    def from_dict(self, data: dict):
        self.enabled = data.get("enabled", True)
        self.mappings.clear()
        for m in data.get("mappings", []):
            mapping = KeyMapping.from_dict(m)
            self.mappings[mapping.source_key] = mapping


class BaseMode(ABC):
    """模式基类 - 每个模式继承此类"""

    def __init__(self, name: str, color: str):
        self.name = name
        self.color = color
        self.mappings: Dict[str, KeyMapping] = {}  # source_key -> KeyMapping
        self.enabled = True
        self.keyboard_ctrl = KeyboardController()
        self.action_executor = ActionExecutor()  # 动作执行器
        self.on_hint: Optional[Callable[[str], None]] = None  # 提示回调

    @abstractmethod
    def get_default_mappings(self) -> list:
        """返回默认映射列表，子类实现"""
        pass

    def add_mapping(self, source: str, target: str, block: bool = True, hint: str = ""):
        """添加映射"""
        self.mappings[source] = KeyMapping(source, target, block, hint)

    def remove_mapping(self, source: str):
        """移除映射"""
        if source in self.mappings:
            del self.mappings[source]

    def get_mapping(self, source: str) -> Optional[str]:
        """获取映射目标"""
        if source in self.mappings:
            return self.mappings[source].target_key
        return None

    def clear_mappings(self):
        """清空所有映射"""
        self.mappings.clear()

    def load_defaults(self):
        """加载默认映射"""
        self.clear_mappings()
        for src, tgt in self.get_default_mappings():
            self.add_mapping(src, tgt)

    def to_dict(self) -> dict:
        """序列化"""
        return {
            "enabled": self.enabled,
            "mappings": [m.to_dict() for m in self.mappings.values()]
        }

    def from_dict(self, data: dict):
        """反序列化"""
        self.enabled = data.get("enabled", True)
        self.mappings.clear()
        for m in data.get("mappings", []):
            mapping = KeyMapping.from_dict(m)
            self.mappings[mapping.source_key] = mapping

    def execute_mapping(self, source_key: str) -> bool:
        """执行按键映射，返回是否屏蔽源按键"""
        if source_key in self.mappings and self.enabled:
            mapping = self.mappings[source_key]

            # 使用动作执行器执行动作
            success = self.action_executor.execute(mapping.action_type, mapping.target_key)

            # 显示提示
            if success and mapping.hint and self.on_hint:
                self.on_hint(mapping.hint)

            return mapping.block  # 返回是否屏蔽
        return False

    def _press_key(self, key_str: str):
        """模拟按键，支持组合键如 alt+tab"""
        keys = self._parse_key_combo(key_str)
        if not keys:
            return
        # 按下所有键
        for key in keys:
            self.keyboard_ctrl.press(key)
        # 反向释放所有键
        for key in reversed(keys):
            self.keyboard_ctrl.release(key)

    def _parse_key_combo(self, key_str: str) -> list:
        """解析按键字符串，支持组合键"""
        special_keys = {
            "space": Key.space, "enter": Key.enter, "tab": Key.tab,
            "backspace": Key.backspace, "delete": Key.delete,
            "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
            "home": Key.home, "end": Key.end, "page_up": Key.page_up, "page_down": Key.page_down,
            "esc": Key.esc, "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
            "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
            "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
            "f13": Key.f13, "f14": Key.f14, "f15": Key.f15, "f16": Key.f16,
            "f17": Key.f17, "f18": Key.f18, "f19": Key.f19, "f20": Key.f20,
            "alt": Key.alt, "alt_l": Key.alt_l, "alt_r": Key.alt_r,
            "ctrl": Key.ctrl, "ctrl_l": Key.ctrl_l, "ctrl_r": Key.ctrl_r,
            "shift": Key.shift, "shift_l": Key.shift_l, "shift_r": Key.shift_r,
            "win": Key.cmd, "cmd": Key.cmd,
        }

        parts = key_str.lower().split("+")
        result = []
        for part in parts:
            part = part.strip()
            if part in special_keys:
                result.append(special_keys[part])
            elif len(part) == 1:
                result.append(KeyCode.from_char(part))
            else:
                return []  # 无法解析
        return result

    def _parse_key(self, key_str: str):
        """解析单个按键字符串"""
        keys = self._parse_key_combo(key_str)
        return keys[0] if len(keys) == 1 else None