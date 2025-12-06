#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
F键监听测试工具
用于测试键盘是否能发送 F13-F20 按键，以及 keyboard 库能否捕获它们
"""

import keyboard
import time
from datetime import datetime


def on_key_event(event):
    """按键事件处理"""
    if event.event_type == 'down':  # 只处理按下事件，避免重复
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{timestamp}] 检测到按键: {event.name.upper():<8} (扫描码: {event.scan_code})")


def main():
    """主函数"""
    print("=" * 60)
    print("  F13-F20 按键监听工具")
    print("=" * 60)
    print("\n正在监听 F13 到 F20 按键...")
    print("提示：按 Ctrl+C 退出程序\n")
    print("-" * 60)

    # 要监听的按键列表
    target_keys = ['f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20']

    # 注册每个按键的监听
    for key in target_keys:
        try:
            keyboard.on_press_key(key, on_key_event)
            print(f"✓ 已注册监听: {key.upper()}")
        except Exception as e:
            print(f"✗ 注册失败: {key.upper()} - {e}")

    print("-" * 60)
    print("\n开始监听，请按下你的 F13-F20 键测试...\n")

    try:
        # 保持程序运行
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n\n程序退出")


if __name__ == "__main__":
    # 检查是否有管理员权限（Windows）
    import sys
    import os

    if os.name == 'nt':
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("警告: 程序可能需要管理员权限才能正常监听全局热键")
                print("建议：右键点击 -> 以管理员身份运行\n")
        except:
            pass

    main()
