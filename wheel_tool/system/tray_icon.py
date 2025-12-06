# -*- coding: utf-8 -*-
"""
系统托盘图标
提供系统托盘图标功能
"""

import threading
import sys
import os
import subprocess
from typing import Optional, Callable
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem


class TrayIcon:
    """系统托盘图标"""

    def __init__(self, on_exit: Optional[Callable] = None, 
                 on_settings: Optional[Callable] = None):
        self.on_exit = on_exit
        self.on_settings = on_settings
        self.icon: Optional[Icon] = None
        self.is_paused = False  # 暂停状态
        self.on_pause_state_changed: Optional[Callable] = None  # 暂停状态变化回调

    def create_icon_image(self) -> Image.Image:
        """创建托盘图标图像"""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # 根据暂停状态改变颜色
        if self.is_paused:
            # 暂停状态：红色
            draw.ellipse([4, 4, size-4, size-4], fill='#ef4444', outline='white', width=2)
            draw.ellipse([24, 24, 40, 40], fill='#333333', outline='white', width=1)
            # 添加暂停符号
            draw.rectangle([20, 20, 28, 44], fill='white')
            draw.rectangle([36, 20, 44, 44], fill='white')
        else:
            # 正常状态：紫色
            draw.ellipse([4, 4, size-4, size-4], fill='#7c3aed', outline='white', width=2)
            draw.ellipse([24, 24, 40, 40], fill='#333333', outline='white', width=1)
        
        return image

    def start(self):
        """启动托盘图标"""
        menu = Menu(
            MenuItem('设置', self._open_settings),
            MenuItem('暂停/恢复', self._toggle_pause),
            MenuItem('重启', self._restart_app),
            MenuItem('退出', self._exit_app)
        )
        self.icon = Icon(
            '圆盘模式切换',
            self.create_icon_image(),
            '圆盘模式切换工具',
            menu
        )
        threading.Thread(target=self.icon.run, daemon=True).start()

    def _toggle_pause(self):
        """切换暂停状态"""
        self.is_paused = not self.is_paused
        
        # 更新图标
        if self.icon:
            self.icon.icon = self.create_icon_image()
            # 更新提示文本
            status = "已暂停" if self.is_paused else "运行中"
            self.icon.title = f"圆盘模式切换工具 - {status}"
        
        # 通知状态变化
        if self.on_pause_state_changed:
            self.on_pause_state_changed(self.is_paused)
        
        print(f"暂停状态: {'已暂停' if self.is_paused else '已恢复'}")

    def _open_settings(self):
        """打开设置"""
        if self.on_settings:
            self.on_settings()

    def _restart_app(self):
        """重启应用"""
        print("准备重启程序...")
        
        if self.icon:
            self.icon.stop()
        
        print("保存配置并清理资源...")
        
        # 重新启动程序
        current_script = sys.argv[0] if sys.argv else __file__
        if not current_script.endswith('.py'):
            current_script = 'wheel_tool.py'
        
        try:
            # 使用subprocess重新启动当前程序
            subprocess.Popen([sys.executable, current_script], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            print("程序重启中...")
            # 延迟退出当前进程，给新进程启动时间
            threading.Timer(1.0, lambda: os._exit(0)).start()
        except Exception as e:
            print(f"重启失败: {e}")
            # 如果subprocess失败，尝试使用os.system
            try:
                if os.name == 'nt':
                    os.system(f'start "" "{sys.executable}" "{current_script}"')
                else:
                    os.system(f'nohup "{sys.executable}" "{current_script}" &')
                threading.Timer(1.0, lambda: os._exit(0)).start()
            except Exception as e2:
                print(f"无法重启程序: {e2}")
                os._exit(0)

    def _exit_app(self):
        """退出应用"""
        if self.icon:
            self.icon.stop()
        if self.on_exit:
            self.on_exit()

    def stop(self):
        """停止托盘图标"""
        if self.icon:
            self.icon.stop()