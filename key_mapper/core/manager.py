# -*- coding: utf-8 -*-
"""
模式管理器
统一管理所有按键映射模式
"""

from typing import List
from .models import BaseMode
from .modes import BrowseMode, MediaMode, VideoMode, WindowMode
from ..config.storage import ConfigManager


class ModeManager:
    """模式管理器"""

    def __init__(self, custom_modes: List[BaseMode] = None):
        self.modes: List[BaseMode] = [
            BrowseMode(),
            MediaMode(),
            VideoMode(),
            WindowMode(),
        ]
        
        # 添加自定义模式
        if custom_modes:
            self.modes.extend(custom_modes)
            
        self.current_index = 0
        self.config = ConfigManager()
        self._load_config()

    def _load_config(self):
        """加载配置"""
        data = self.config.load()
        for mode in self.modes:
            if mode.name in data:
                mode.from_dict(data[mode.name])
            else:
                mode.load_defaults()

    def save_config(self):
        """保存配置"""
        data = {mode.name: mode.to_dict() for mode in self.modes}
        self.config.save(data)

    def get_current_mode(self) -> BaseMode:
        return self.modes[self.current_index]

    def set_current_index(self, index: int):
        self.current_index = index % len(self.modes)

    def set_current_mode_by_name(self, name: str) -> bool:
        """根据模式名称设置当前模式"""
        for i, mode in enumerate(self.modes):
            if mode.name == name:
                self.current_index = i
                return True
        return False

    def handle_key(self, key_str: str) -> bool:
        """处理按键，返回是否被映射处理"""
        return self.get_current_mode().execute_mapping(key_str)

    def get_mode_by_name(self, name: str) -> BaseMode:
        """根据名称获取模式"""
        for mode in self.modes:
            if mode.name == name:
                return mode
        raise ValueError(f"未找到模式: {name}")

    def add_mode(self, mode: BaseMode):
        """添加新模式"""
        self.modes.append(mode)

    def remove_mode(self, name: str) -> bool:
        """移除模式"""
        for i, mode in enumerate(self.modes):
            if mode.name == name:
                del self.modes[i]
                # 调整当前索引
                if self.current_index >= len(self.modes) and self.current_index > 0:
                    self.current_index = len(self.modes) - 1
                return True
        return False

    def get_mode_names(self) -> List[str]:
        """获取所有模式名称"""
        return [mode.name for mode in self.modes]