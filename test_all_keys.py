#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局按键监听工具
监听并显示所有按键的输入情况，包括按键名称和扫描码
"""

import keyboard
from datetime import datetime
from collections import defaultdict


class KeyMonitor:
    """按键监听器"""

    def __init__(self):
        self.key_counts = defaultdict(int)  # 统计每个按键的按下次数
        self.last_keys = []  # 记录最近按下的按键
        self.max_history = 10  # 最多显示最近10个按键

    def on_key_down(self, event):
        """按键按下事件"""
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        key_name = event.name.upper()
        scan_code = event.scan_code

        # 更新统计
        self.key_counts[key_name] += 1
        count = self.key_counts[key_name]

        # 特殊标记 F13-F20
        is_special = key_name in ['F13', 'F14', 'F15', 'F16', 'F17', 'F18', 'F19', 'F20']
        marker = " ⭐" if is_special else ""

        # 显示按键信息
        print(f"[{timestamp}] {key_name:<12} (扫描码: {scan_code:>4}) - 第 {count} 次{marker}")

        # 记录到历史
        self.last_keys.append(key_name)
        if len(self.last_keys) > self.max_history:
            self.last_keys.pop(0)

    def show_summary(self):
        """显示统计摘要"""
        print("\n" + "=" * 60)
        print("按键统计摘要：")
        print("-" * 60)

        if not self.key_counts:
            print("  (没有记录到任何按键)")
        else:
            # 按次数排序
            sorted_keys = sorted(self.key_counts.items(), key=lambda x: x[1], reverse=True)
            for key, count in sorted_keys[:20]:  # 只显示前20个
                is_special = key in ['F13', 'F14', 'F15', 'F16', 'F17', 'F18', 'F19', 'F20']
                marker = " ⭐" if is_special else ""
                print(f"  {key:<12} : {count:>3} 次{marker}")

        print("\n最近按键序列：")
        print("  " + " → ".join(self.last_keys[-10:]) if self.last_keys else "  (无)")
        print("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("  全局按键监听工具")
    print("=" * 60)
    print("\n功能：监听并显示所有按键输入")
    print("特别关注：F13-F20 会用 ⭐ 标记")
    print("\n提示：")
    print("  - 按任意键测试")
    print("  - 按 ESC 显示统计并退出")
    print("  - 按 Ctrl+C 强制退出")
    print("-" * 60)
    print()

    monitor = KeyMonitor()

    # 注册按键监听
    keyboard.on_press(monitor.on_key_down)

    try:
        # 等待 ESC 键退出
        keyboard.wait('esc')
        print("\n检测到 ESC 键，准备退出...\n")
        monitor.show_summary()

    except KeyboardInterrupt:
        print("\n\n检测到 Ctrl+C，准备退出...\n")
        monitor.show_summary()


if __name__ == "__main__":
    import sys
    import os

    # 检查管理员权限
    if os.name == 'nt':
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("⚠️  警告: 建议以管理员身份运行以确保能监听所有按键\n")
        except:
            pass

    main()
