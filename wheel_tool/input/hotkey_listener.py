# -*- coding: utf-8 -*-
"""
全局热键监听模块
提供跨平台热键监听功能
"""

import keyboard as kb
from typing import Optional, Callable, Any
from ..ui.hint_overlay import HintOverlay
from ..config.settings import GlobalConfig


class HotkeyListener:
    """全局热键监听器 - 使用keyboard库(跨平台)"""

    def __init__(self, disk, controller, mode_manager=None, settings_panel=None):
        self.disk = disk
        self.controller = controller
        self.mode_manager = mode_manager
        self.settings_panel = settings_panel
        self.running = False
        self.is_paused = False  # 暂停状态
        self.hint_overlay = None  # 提示悬浮窗

    def set_pause_state(self, paused: bool):
        """设置暂停状态"""
        self.is_paused = paused
        status = "已暂停" if paused else "已恢复"
        print(f"热键监听器{status}")

    def start(self):
        """开始监听"""
        self.running = True

        # 创建提示悬浮窗（传入父窗口避免空白窗口）
        self.hint_overlay = HintOverlay(parent=self.disk.root)
        self.hint_overlay.create_window()

        # 从配置文件读取热键设置
        prev_mode_key = GlobalConfig.get('hotkeys.prev_mode', 'ctrl+alt+shift+=')
        next_mode_key = GlobalConfig.get('hotkeys.next_mode', 'ctrl+alt+shift+-')
        open_settings_key = GlobalConfig.get('hotkeys.open_settings', 'ctrl+alt+shift+s')
        hide_disk_key = GlobalConfig.get('hotkeys.hide_disk', 'esc')

        # 注册热键组合
        kb.add_hotkey(prev_mode_key, lambda: self._handle_mode_switch('prev'))
        kb.add_hotkey(next_mode_key, lambda: self._handle_mode_switch('next'))
        kb.add_hotkey(open_settings_key, lambda: self.disk.root.after(0, self._open_settings))
        kb.add_hotkey(hide_disk_key, lambda: self.disk.root.after(0, self.disk.hide))

        # 注册需要屏蔽的映射按键
        self._register_mapped_keys()

        print("热键监听已启动:")
        print(f"  {prev_mode_key.upper():<25}: 上一模式")
        print(f"  {next_mode_key.upper():<25}: 下一模式")
        print(f"  {open_settings_key.upper():<25}: 打开设置面板")
        print(f"  {hide_disk_key.upper():<25}: 隐藏圆盘")

    def _handle_mode_switch(self, direction):
        """处理模式切换"""
        if self.is_paused:
            print(f"暂停状态中，无法切换{direction}模式")
            return
        
        if direction == 'prev':
            self.disk.root.after(0, self.disk.prev_mode)
        else:
            self.disk.root.after(0, self.disk.next_mode)

    def _register_mapped_keys(self):
        """为所有可能的映射按键注册钩子"""
        # 收集所有模式中的源按键
        all_keys = set()
        if self.mode_manager:
            for mode in self.mode_manager.modes:
                for key in mode.mappings.keys():
                    all_keys.add(key)

        # 为每个按键注册带suppress的钩子
        for key in all_keys:
            kb.on_press_key(key, lambda e, k=key: self._handle_mapped_key(k), suppress=True)

    def _handle_mapped_key(self, key_name):
        """处理映射按键"""
        # 如果暂停状态，直接发送原按键
        if self.is_paused:
            kb.send(key_name)
            return

        if not self.mode_manager:
            kb.send(key_name)
            return

        # 检查映射
        self.mode_manager.set_current_index(self.disk.current_mode)
        mode = self.mode_manager.get_current_mode()

        if mode.enabled and key_name in mode.mappings:
            mapping = mode.mappings[key_name]

            # 使用新的 execute_mapping 方法（支持不同的 action_type）
            # 这会自动处理 keyboard、mouse_scroll、mouse_click、command 等类型
            should_block = mode.execute_mapping(key_name)

            print(f"  -> 映射执行: {key_name} -> {mapping.target_key} (类型: {mapping.action_type})")

            # 显示提示文本（已经在 execute_mapping 中处理，这里保留兼容性）
            if self.hint_overlay and hasattr(mapping, 'hint') and mapping.hint:
                try:
                    self.disk.root.after(0, lambda: self.hint_overlay.show(mapping.hint))
                except:
                    pass

            # 如果不屏蔽，发送原按键
            if not should_block:
                kb.send(key_name)
        else:
            # 没有映射，发送原按键
            kb.send(key_name)

    def _open_settings(self):
        """打开设置面板"""
        if self.settings_panel:
            self.settings_panel.show()

    def stop(self):
        """停止监听"""
        if self.running:
            kb.unhook_all()
            self.running = False

            # 销毁提示窗口
            if self.hint_overlay:
                try:
                    self.hint_overlay.destroy()
                except:
                    pass
                self.hint_overlay = None