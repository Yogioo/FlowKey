# -*- coding: utf-8 -*-
"""
主程序入口
应用程序的核心控制和生命周期管理
"""

import signal
import sys
import threading
import time
import os
import subprocess
from typing import Optional, Callable

from .tray_icon import TrayIcon
from ..config.settings import GlobalConfig


class WheelToolApp:
    """应用程序主类"""
    
    def __init__(self, mode_manager=None, disk=None, listener=None, settings_panel=None):
        self.mode_manager = mode_manager
        self.disk = disk
        self.listener = listener
        self.settings_panel = settings_panel
        self.tray_icon = None
        self.running = False
        self._setup_tray_icon()
        
    def _setup_tray_icon(self):
        """设置系统托盘图标"""
        def on_exit():
            self.cleanup()
            
        def on_settings():
            if self.settings_panel and self.disk:
                self.disk.root.after(0, self.settings_panel.show)
        
        def on_pause_state_changed(paused: bool):
            if self.listener:
                self.listener.set_pause_state(paused)
        
        self.tray_icon = TrayIcon(on_exit, on_settings)
        self.tray_icon.on_pause_state_changed = on_pause_state_changed

    def start(self):
        """启动应用程序"""
        if self.running:
            return

        self.running = True
        print("=" * 40)
        print("  圆盘模式切换工具 v2.0")
        print("  支持快捷键映射配置")
        print("=" * 40)
        print("  按 Ctrl+C 退出")

        # 先创建圆盘窗口（必须在热键监听之前，因为 HintOverlay 需要父窗口）
        if self.disk:
            self.disk.create_window()

        # 启动托盘图标
        if self.tray_icon:
            self.tray_icon.start()

        # 启动热键监听（必须在 disk.create_window() 之后）
        if self.listener:
            self.listener.start()

        # 设置信号处理
        self._setup_signal_handlers()

        # 启动主循环
        self._run_main_loop()

    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(sig, frame):
            if self.disk:
                self.disk.root.after(0, self.cleanup)
        
        signal.signal(signal.SIGINT, signal_handler)

    def _run_main_loop(self):
        """运行主循环"""
        def check_interrupt():
            """定期检查以响应信号"""
            if self.disk and self.running:
                self.disk.root.after(100, check_interrupt)

        if self.disk:
            check_interrupt()
            try:
                self.disk.root.mainloop()
            except KeyboardInterrupt:
                self.cleanup()

    def cleanup(self):
        """清理并退出"""
        if not self.running:
            return
            
        print("\n程序退出")
        self.running = False
        
        # 保存配置
        if self.mode_manager:
            self.mode_manager.save_config()
        
        # 停止各个组件
        if self.listener:
            self.listener.stop()
        
        if self.tray_icon:
            self.tray_icon.stop()
        
        if self.disk and self.disk.root:
            self.disk.root.quit()
        
        sys.exit(0)

    def restart(self):
        """重启应用程序"""
        print("准备重启程序...")
        
        # 清理当前实例
        if self.tray_icon:
            self.tray_icon.stop()
        
        # 保存配置
        if self.mode_manager:
            self.mode_manager.save_config()
        
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
            # 延迟退出当前进程
            threading.Timer(1.0, lambda: os._exit(0)).start()
        except Exception as e:
            print(f"重启失败: {e}")
            # 备用重启方式
            try:
                if os.name == 'nt':
                    os.system(f'start "" "{sys.executable}" "{current_script}"')
                else:
                    os.system(f'nohup "{sys.executable}" "{current_script}" &')
                threading.Timer(1.0, lambda: os._exit(0)).start()
            except Exception as e2:
                print(f"无法重启程序: {e2}")
                os._exit(0)

    def is_running(self) -> bool:
        """检查应用是否正在运行"""
        return self.running

    def get_status(self) -> dict:
        """获取应用状态信息"""
        status = {
            "running": self.running,
            "tray_icon": self.tray_icon is not None and hasattr(self.tray_icon, 'icon'),
            "pause_state": self.tray_icon.is_paused if self.tray_icon else False,
            "current_mode": self.disk.current_mode if self.disk else None,
            "listener_running": self.listener.running if self.listener else False,
        }
        return status