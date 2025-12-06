# -*- coding: utf-8 -*-
"""
测试映射面板的功能
"""

import sys
import tkinter as tk

# 导入必要的模块
from key_mapper.core.manager import ModeManager
from key_mapper.ui.mapping_panel import MappingPanel


def test_panel_creation():
    """测试面板创建"""
    print("1. 测试面板创建...")

    # 创建模式管理器
    mode_manager = ModeManager()
    print(f"   ✓ 模式管理器创建成功，共{len(mode_manager.modes)}个模式")

    # 创建面板
    panel = MappingPanel(mode_manager)
    print("   ✓ 映射面板创建成功")

    # 检查必要的控件属性
    required_attrs = [
        'target_keyboard_frame',
        'target_mouse_scroll_frame',
        'target_mouse_click_frame',
        'target_window_cycle_frame',
        'target_command_frame',
        'action_type_display_map',
        'action_type_code_map'
    ]

    for attr in required_attrs:
        if not hasattr(panel, attr):
            print(f"   ✗ 缺少属性: {attr}")
            return False
        print(f"   ✓ 属性 {attr} 存在")

    print("   ✓ 所有必要属性都存在")
    return True


def test_mapping_creation():
    """测试不同类型映射的创建"""
    print("\n2. 测试映射创建...")

    from key_mapper.core.models import KeyMapping

    # 测试各种类型的映射
    test_cases = [
        ("keyboard", "f13", "ctrl+w", "关闭标签"),
        ("mouse_scroll", "f14", "down:3", "向下滚动"),
        ("mouse_click", "f15", "left", "左键点击"),
        ("window_cycle", "f16", "next", "下一个窗口"),
        ("command", "f17", "notepad.exe", "打开记事本")
    ]

    for action_type, source, target, hint in test_cases:
        mapping = KeyMapping(source, target, True, hint, action_type)
        print(f"   ✓ {action_type}: {source} -> {target}")

        # 验证序列化
        data = mapping.to_dict()
        assert data['action_type'] == action_type
        assert data['source'] == source
        assert data['target'] == target

        # 验证反序列化
        restored = KeyMapping.from_dict(data)
        assert restored.action_type == action_type
        assert restored.source_key == source
        assert restored.target_key == target

    print("   ✓ 所有映射类型创建和序列化测试通过")
    return True


def test_window_mode_defaults():
    """测试窗口管理模式的默认映射"""
    print("\n3. 测试窗口管理模式...")

    from key_mapper.core.modes import WindowMode

    mode = WindowMode()
    mode.load_defaults()

    print(f"   模式名称: {mode.name}")
    print(f"   默认映射数量: {len(mode.mappings)}")

    for source, mapping in mode.mappings.items():
        print(f"   {source}: {mapping.target_key} (类型: {mapping.action_type})")
        assert mapping.action_type == "window_cycle"
        assert mapping.target_key in ["next", "prev"]

    print("   ✓ 窗口管理模式默认映射正确")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("开始测试映射面板功能...")
    print("=" * 60)

    try:
        # 运行所有测试
        tests = [
            test_panel_creation,
            test_mapping_creation,
            test_window_mode_defaults
        ]

        all_passed = True
        for test in tests:
            if not test():
                all_passed = False
                print(f"✗ {test.__name__} 失败")

        print("\n" + "=" * 60)
        if all_passed:
            print("✓ 所有测试通过!")
        else:
            print("✗ 部分测试失败")
        print("=" * 60)

        sys.exit(0 if all_passed else 1)

    except Exception as e:
        print(f"\n✗ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
