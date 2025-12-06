# -*- coding: utf-8 -*-
"""
测试虚拟桌面过滤功能
"""

import sys
sys.path.insert(0, r"E:\Desktop\f")

from key_mapper.utils.window_cycler import WindowCycler


def test_virtual_desktop_filtering():
    """测试虚拟桌面过滤"""
    print("=" * 60)
    print("测试虚拟桌面过滤")
    print("=" * 60)

    cycler = WindowCycler()
    cycler.refresh_windows()

    print(f"\n当前虚拟桌面的窗口列表 (共 {len(cycler.windows)} 个):")
    for i, win in enumerate(cycler.windows):
        marker = " ← 当前" if i == cycler.current_index else ""
        print(f"  [{i}] {win.title}{marker}")

    print("\n如果你有多个虚拟桌面，请切换到另一个桌面的窗口，")
    print("然后再运行这个测试，看看窗口数量是否减少。")


if __name__ == "__main__":
    try:
        test_virtual_desktop_filtering()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
