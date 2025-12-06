# -*- coding: utf-8 -*-
"""
测试上一个窗口切换的问题
"""

import sys
import time
sys.path.insert(0, r"E:\Desktop\f")

from key_mapper.utils.window_cycler import WindowCycler


def test_prev_issue():
    """测试 prev 切换问题"""
    print("=" * 60)
    print("测试上一个窗口切换")
    print("=" * 60)

    cycler = WindowCycler()
    cycler.refresh_windows()

    print(f"\n初始窗口列表 (共 {len(cycler.windows)} 个):")
    for i, win in enumerate(cycler.windows):
        marker = " ← 当前" if i == cycler.current_index else ""
        print(f"  [{i}] {win.title}{marker}")

    print(f"\n当前索引: {cycler.current_index}")
    print("\n开始测试连续 prev 切换...")

    for test_num in range(5):
        print(f"\n--- 第 {test_num + 1} 次 prev ---")
        print(f"切换前索引: {cycler.current_index}")

        # 执行 prev
        result = cycler.switch_prev()

        if result:
            print(f"切换后索引: {cycler.current_index}")
            print(f"切换到: {result.title}")

            # 再次获取前台窗口，验证是否真的切换了
            time.sleep(0.2)  # 等待窗口切换完成
            current = cycler.get_current_window()
            if current:
                print(f"验证前台窗口: {current.title}")
                if current.hwnd != result.hwnd:
                    print("⚠️ 警告：切换的窗口与实际前台窗口不一致！")
        else:
            print("✗ 切换失败")

        time.sleep(1)  # 等待一秒再进行下次切换


if __name__ == "__main__":
    try:
        test_prev_issue()
        print("\n测试完成！")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
