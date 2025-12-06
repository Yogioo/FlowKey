# -*- coding: utf-8 -*-
"""
应用级配置
管理wheel_tool应用的全局配置
"""

import os
import json
from typing import Dict, Any


class AppSettings:
    """应用设置类"""
    
    def __init__(self):
        self.config_file = "wheel_tool_config.json"
        self.config_path = os.path.join(os.path.dirname(__file__), "..", "..", self.config_file)
        self._default_config = self._get_default_config()
        self._config = {}

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "window": {
    "alpha": 1.0,
                "size": 320,
                "center_on_screen": True
            },
            "display": {
                "fade_step": 20,
                "hide_delay": 600,
            },
            "hint_overlay": {
                "enabled": True,
                "width": 400,
                "height": 80,
                "alpha": 0.85,
                "display_duration": 1200,
                "bottom_margin": 100,
                "font_size": 24,
                "background_color": "#2a2a2a",
                "text_color": "#ffffff",
                "border_radius": 12
            },
            "hotkeys": {
                "next_mode": "ctrl+alt+shift+-",
                "prev_mode": "ctrl+alt+shift+=",
                "open_settings": "ctrl+alt+shift+s",
                "hide_disk": "esc"
            },
            "tray": {
                "enable": True,
                "show_notifications": False
            }
        }

    def load(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                # 合并默认配置和加载的配置
                config = self._default_config.copy()
                self._deep_update(config, loaded_config)
                self._config = config
                return config
            except Exception as e:
                print(f"加载应用配置失败: {e}")
        
        self._config = self._default_config.copy()
        return self._config

    def save(self, config: Dict[str, Any] = None):
        """保存配置"""
        if config is None:
            config = self._config
        
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存应用配置失败: {e}")

    def get(self, key_path: str, default=None):
        """获取配置值，支持点号分隔的路径"""
        keys = key_path.split(".")
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

    def set(self, key_path: str, value: Any):
        """设置配置值，支持点号分隔的路径"""
        keys = key_path.split(".")
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value

    def _deep_update(self, base_dict: Dict, update_dict: Dict):
        """深度更新字典"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value


class GlobalConfig:
    """全局配置单例"""
    
    _instance = None
    _settings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(cls):
        if cls._settings is None:
            cls._settings = AppSettings()

    def __init__(self):
        if self._settings is None:
            self._settings = AppSettings()

    @classmethod
    def _get_instance(cls):
        """获取实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def load(cls):
        """加载配置"""
        return cls._get_instance()._settings.load()

    @classmethod
    def save(cls, config=None):
        """保存配置"""
        cls._get_instance()._settings.save(config)

    @classmethod
    def get(cls, key_path: str, default=None):
        """获取配置值"""
        return cls._get_instance()._settings.get(key_path, default)

    @classmethod
    def set(cls, key_path: str, value):
        """设置配置值"""
        cls._get_instance()._settings.set(key_path, value)