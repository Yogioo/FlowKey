# -*- coding: utf-8 -*-
"""
配置管理
负责配置的读取、写入和管理
"""

import json
import os


class ConfigManager:
    """配置管理器 - 持久化存储"""

    CONFIG_FILE = "key_mappings.json"

    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "..", "..", self.CONFIG_FILE)

    def load(self) -> dict:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置失败: {e}")
                return {}
        return {}

    def save(self, config: dict):
        """保存配置"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")


def load_config() -> dict:
    """加载配置的便捷函数"""
    manager = ConfigManager()
    return manager.load()


def save_config(config: dict):
    """保存配置的便捷函数"""
    manager = ConfigManager()
    manager.save(config)