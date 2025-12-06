# -*- coding: utf-8 -*-
"""
动作执行器模块
实现不同类型的动作执行：键盘、鼠标、系统命令等
"""

import subprocess
import sys
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key, KeyCode

# Windows 特定的鼠标滚轮支持
if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes

    # Windows 常量
    MOUSEEVENTF_WHEEL = 0x0800
    WHEEL_DELTA = 120  # Windows 标准滚轮单位

    # 导入窗口切换器
    from key_mapper.utils.window_cycler import WindowCycler


class ActionExecutor:
    """动作执行器基类"""

    def __init__(self):
        self.keyboard_ctrl = KeyboardController()
        self.mouse_ctrl = MouseController()
        # Windows 窗口切换器
        if sys.platform == 'win32':
            self.window_cycler = WindowCycler()
        else:
            self.window_cycler = None

    def execute(self, action_type: str, target: str) -> bool:
        """
        执行动作

        Args:
            action_type: 动作类型 (keyboard, mouse_scroll, mouse_click, command, window_cycle)
            target: 目标动作描述

        Returns:
            bool: 执行是否成功
        """
        try:
            if action_type == "keyboard":
                return self.execute_keyboard(target)
            elif action_type == "mouse_scroll":
                return self.execute_mouse_scroll(target)
            elif action_type == "mouse_click":
                return self.execute_mouse_click(target)
            elif action_type == "command":
                return self.execute_command(target)
            elif action_type == "window_cycle":
                return self.execute_window_cycle(target)
            else:
                print(f"[执行器] 未知的动作类型: {action_type}")
                return False
        except Exception as e:
            print(f"[执行器] 执行动作失败 ({action_type}): {e}")
            return False

    def execute_keyboard(self, target: str) -> bool:
        """
        执行键盘按键操作

        Args:
            target: 按键组合，如 "ctrl+w" 或 "alt+tab"

        Returns:
            bool: 执行是否成功
        """
        keys = self._parse_key_combo(target)
        if not keys:
            print(f"[执行器] 无法解析按键: {target}")
            return False

        # 按下所有键
        for key in keys:
            self.keyboard_ctrl.press(key)

        # 反向释放所有键
        for key in reversed(keys):
            self.keyboard_ctrl.release(key)

        return True

    def execute_mouse_scroll(self, target: str) -> bool:
        """
        执行鼠标滚轮操作

        Args:
            target: 滚动描述，格式 "down:3" 或 "up:5"
                   - down/up: 滚动方向
                   - 数字: 滚动量

        Returns:
            bool: 执行是否成功
        """
        print(f"[执行器] 准备执行鼠标滚轮: {target}")
        parts = target.lower().split(':')
        direction = parts[0].strip()
        amount = int(parts[1].strip()) if len(parts) > 1 else 1

        print(f"[执行器] 解析结果 - 方向: {direction}, 滚动量: {amount}")

        # 在 Windows 上使用原生 API 以获得更好的效果
        if sys.platform == 'win32':
            return self._windows_scroll(direction, amount)
        else:
            # 其他平台使用 pynput
            if direction == 'down':
                self.mouse_ctrl.scroll(0, -amount)
                return True
            elif direction == 'up':
                self.mouse_ctrl.scroll(0, amount)
                return True
            else:
                print(f"[执行器] 未知的滚动方向: {direction}")
                return False

    def _windows_scroll(self, direction: str, amount: int) -> bool:
        """Windows 特定的滚轮实现"""
        try:
            # Windows 使用 mouse_event 实现滚轮
            # WHEEL_DELTA (120) 是标准滚轮单位
            if direction == 'down':
                delta = -WHEEL_DELTA * amount
            elif direction == 'up':
                delta = WHEEL_DELTA * amount
            else:
                print(f"[执行器] 未知的滚动方向: {direction}")
                return False

            print(f"[执行器] Windows API 滚轮: delta={delta}")
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
            print(f"[执行器] 滚轮操作已执行")
            return True
        except Exception as e:
            print(f"[执行器] Windows 滚轮失败: {e}")
            return False

    def execute_mouse_click(self, target: str) -> bool:
        """
        执行鼠标点击操作

        Args:
            target: 鼠标按钮，可选 "left", "right", "middle"

        Returns:
            bool: 执行是否成功
        """
        button_map = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle
        }

        target = target.lower().strip()
        button = button_map.get(target)

        if button:
            self.mouse_ctrl.click(button)
            return True
        else:
            print(f"[执行器] 未知的鼠标按钮: {target}")
            return False

    def execute_command(self, target: str) -> bool:
        """
        执行系统命令

        Args:
            target: 要执行的命令，如 "shutdown /s /t 0"

        Returns:
            bool: 执行是否成功
        """
        try:
            # 使用 Popen 异步执行，避免阻塞
            subprocess.Popen(target, shell=True)
            print(f"[执行器] 执行命令: {target}")
            return True
        except Exception as e:
            print(f"[执行器] 命令执行失败: {e}")
            return False

    def _parse_key_combo(self, key_str: str) -> list:
        """
        解析按键字符串，支持组合键

        Args:
            key_str: 按键字符串，如 "ctrl+w" 或 "alt+tab"

        Returns:
            list: 解析后的按键对象列表
        """
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

    def execute_window_cycle(self, target: str) -> bool:
        """
        执行窗口循环切换操作

        Args:
            target: 切换方向，可选 "next" (下一个窗口) 或 "prev" (上一个窗口)

        Returns:
            bool: 执行是否成功
        """
        if not self.window_cycler:
            print("[执行器] 窗口切换器不可用 (仅支持 Windows)")
            return False

        target = target.lower().strip()

        if target == "next":
            result = self.window_cycler.switch_next()
            return result is not None
        elif target == "prev":
            result = self.window_cycler.switch_prev()
            return result is not None
        else:
            print(f"[执行器] 未知的窗口切换方向: {target}")
            return False

