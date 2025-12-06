# -*- coding: utf-8 -*-
"""
测试窗口切换器功能
"""

import sys
import time

# 添加项目路径
sys.path.insert(0, r"E:\Desktop\f")

from key_mapper.utils.window_cycler import WindowCycler


def test_window_list():
    """测试获取窗口列表"""
    print("=== 测试窗口列表 ===")
    cycler = WindowCycler()
    cycler.refresh_windows()

    windows = cycler.get_window_list()
    print(f"找到 {len(windows)} 个窗口：")
    for i, win in enumerate(windows):
        print(f"  {i+1}. {win.title} (hwnd={win.hwnd})")

    current = cycler.get_current_window()
    if current:
        print(f"\n当前活动窗口: {current.title}")


def test_window_switch():
    """测试窗口切换"""
    print("\n=== 测试窗口切换 ===")
    cycler = WindowCycler()

    print("将在 2 秒后开始切换窗口...")
    time.sleep(2)

    print("\n切换到下一个窗口...")
    next_win = cycler.switch_next()
    if next_win:
        print(f"✓ 切换成功: {next_win.title}")
    else:
        print("✗ 切换失败")

    time.sleep(2)

    print("\n切换到上一个窗口...")
    prev_win = cycler.switch_prev()
    if prev_win:
        print(f"✓ 切换成功: {prev_win.title}")
    else:
        print("✗ 切换失败")


def test_cyclic_switch():
    """测试循环切换"""
    print("\n=== 测试循环切换 ===")
    cycler = WindowCycler()
    cycler.refresh_windows()

    window_count = len(cycler.windows)
    print(f"共有 {window_count} 个窗口，将循环切换...")
    time.sleep(2)

    for i in range(min(5, window_count)):  # 最多切换5次
        print(f"\n第 {i+1} 次切换...")
        win = cycler.switch_next()
        if win:
            print(f"  当前窗口: {win.title}")
        time.sleep(1.5)


def test_action_executor():
    """测试 ActionExecutor 集成"""
    print("\n=== 测试 ActionExecutor 集成 ===")
    from key_mapper.core.executors import ActionExecutor

    executor = ActionExecutor()

    print("测试 window_cycle next...")
    time.sleep(2)
    result = executor.execute("window_cycle", "next")
    print(f"执行结果: {'成功' if result else '失败'}")

    time.sleep(2)
    print("\n测试 window_cycle prev...")
    result = executor.execute("window_cycle", "prev")
    print(f"执行结果: {'成功' if result else '失败'}")


def test_window_mode():
    """测试 WindowMode 配置"""
    print("\n=== 测试 WindowMode 配置 ===")
    from key_mapper.core.modes import WindowMode

    mode = WindowMode()
    mode.load_defaults()

    print("WindowMode 默认映射：")
    for source, mapping in mode.mappings.items():
        print(f"  {source} -> {mapping.target_key} (类型: {mapping.action_type}, 提示: {mapping.hint})")

    # 测试执行映射
    print("\n测试执行 f24 映射 (下一个窗口)...")
    time.sleep(2)
    mode.execute_mapping("f24")

    time.sleep(2)
    print("\n测试执行 f23 映射 (上一个窗口)...")
    mode.execute_mapping("f23")


if __name__ == "__main__":
    print("窗口切换器测试\n")

    try:
        # 测试1: 窗口列表
        test_window_list()

        # 测试2: 基本切换
        test_window_switch()

        # 测试3: 循环切换
        # test_cyclic_switch()

        # 测试4: ActionExecutor 集成
        test_action_executor()

        # 测试5: WindowMode 配置
        test_window_mode()

        print("\n✓ 所有测试完成！")

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
