# -*- coding: utf-8 -*-
"""
开机启动管理模块
管理应用的开机自动启动功能（Windows）
"""

import os
import sys
import winreg
from pathlib import Path


class StartupManager:
    """开机启动管理器"""

    # 注册表路径：当前用户的启动项
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    # 应用名称（用作注册表键名）
    APP_NAME = "WheelDiskTool"

    @classmethod
    def get_executable_path(cls) -> str:
        """
        获取当前可执行文件的完整路径

        Returns:
            str: 可执行文件路径
        """
        # 如果是打包后的exe文件
        if getattr(sys, 'frozen', False):
            return sys.executable

        # 如果是Python脚本，返回Python解释器 + 脚本路径
        script_path = Path(__file__).parent.parent.parent / "main.py"
        python_exe = sys.executable
        return f'"{python_exe}" "{script_path.absolute()}"'

    @classmethod
    def is_enabled(cls) -> bool:
        """
        检查开机启动是否已启用

        Returns:
            bool: True表示已启用，False表示未启用
        """
        try:
            # 打开注册表键
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                winreg.KEY_READ
            )

            try:
                # 尝试读取注册表值
                value, _ = winreg.QueryValueEx(key, cls.APP_NAME)
                winreg.CloseKey(key)

                # 检查路径是否与当前程序一致
                current_path = cls.get_executable_path()
                return value == current_path

            except FileNotFoundError:
                # 键不存在
                winreg.CloseKey(key)
                return False

        except Exception as e:
            print(f"检查开机启动状态失败: {e}")
            return False

    @classmethod
    def enable(cls) -> bool:
        """
        启用开机启动

        Returns:
            bool: True表示成功，False表示失败
        """
        try:
            # 获取可执行文件路径
            exe_path = cls.get_executable_path()

            # 打开注册表键（如果不存在则创建）
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                winreg.KEY_WRITE
            )

            # 设置注册表值
            winreg.SetValueEx(
                key,
                cls.APP_NAME,
                0,
                winreg.REG_SZ,
                exe_path
            )

            winreg.CloseKey(key)
            print(f"✅ 开机启动已启用: {exe_path}")
            return True

        except Exception as e:
            print(f"❌ 启用开机启动失败: {e}")
            return False

    @classmethod
    def disable(cls) -> bool:
        """
        禁用开机启动

        Returns:
            bool: True表示成功，False表示失败
        """
        try:
            # 打开注册表键
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                cls.REG_PATH,
                0,
                winreg.KEY_WRITE
            )

            try:
                # 删除注册表值
                winreg.DeleteValue(key, cls.APP_NAME)
                winreg.CloseKey(key)
                print("✅ 开机启动已禁用")
                return True

            except FileNotFoundError:
                # 键不存在，认为已经是禁用状态
                winreg.CloseKey(key)
                return True

        except Exception as e:
            print(f"❌ 禁用开机启动失败: {e}")
            return False

    @classmethod
    def toggle(cls, enabled: bool) -> bool:
        """
        切换开机启动状态

        Args:
            enabled: True表示启用，False表示禁用

        Returns:
            bool: True表示操作成功，False表示失败
        """
        if enabled:
            return cls.enable()
        else:
            return cls.disable()


# 测试代码
if __name__ == "__main__":
    print("当前开机启动状态:", StartupManager.is_enabled())
    print("可执行文件路径:", StartupManager.get_executable_path())
