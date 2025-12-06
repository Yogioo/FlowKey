#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试轮盘修复后的功能
"""

import sys
import threading
import time
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from wheel_tool.ui.disk import WheelDisk
from wheel_tool.config.settings import GlobalConfig


def test_disk_fixes():
    """测试修复后的轮盘功能"""
    print("🔧 测试轮盘修复后的功能...")
    
    # 创建轮盘实例
    disk = WheelDisk()
    disk.create_window()
    print("✅ 轮盘窗口创建成功")
    
    # 测试1: 置顶功能
    print("\n📌 测试置顶功能...")
    disk.show()
    print("✅ 轮盘已显示，应该在最前面")
    
    # 等待用户观察置顶效果
    input("按Enter继续测试自动隐藏功能...")
    
    # 测试2: 自动隐藏功能
    print("\n⏰ 测试自动隐藏功能...")
    print(f"设置hide_delay为3秒进行测试")
    
    # 临时设置较短的超时时间用于测试
    disk.set_display_config({'hide_delay': 3000})
    
    disk.show()
    print("✅ 轮盘已显示，应该在3秒后自动隐藏...")
    
    # 等待自动隐藏
    time.sleep(4)
    if not disk.visible:
        print("✅ 自动隐藏功能正常工作")
    else:
        print("❌ 自动隐藏功能有问题")
    
    # 测试3: 模式切换效果
    print("\n🔄 测试模式切换效果...")
    disk.show()
    print(f"当前模式: {disk.MODES[disk.current_mode]}")
    
    # 测试切换到下一个模式
    print("切换到下一个模式...")
    disk.next_mode()
    print(f"新模式: {disk.MODES[disk.current_mode]}")
    time.sleep(2)
    
    # 测试切换到上一个模式
    print("切换到上一个模式...")
    disk.prev_mode()
    print(f"新模式: {disk.MODES[disk.current_mode]}")
    time.sleep(2)
    
    # 测试连续切换
    print("连续切换4次模式...")
    for i in range(4):
        disk.next_mode()
        print(f"第{i+1}次切换: {disk.MODES[disk.current_mode]}")
        time.sleep(1)
    
    print("\n✅ 模式切换效果测试完成")
    
    # 清理
    disk.root.destroy()
    print("🧹 清理完成")


def test_display_config():
    """测试显示配置"""
    print("\n⚙️ 测试显示配置...")
    
    config = GlobalConfig.load()
    display_config = config.get('display', {})
    print(f"当前显示配置: {display_config}")
    
    # 测试配置更新
    GlobalConfig.set('display.fade_step', 25)
    GlobalConfig.set('display.hide_delay', 800)
    GlobalConfig.save()
    
    updated_config = GlobalConfig.load().get('display', {})
    print(f"更新后的显示配置: {updated_config}")
    
    print("✅ 显示配置测试完成")


def main():
    """主函数"""
    print("=" * 60)
    print("轮盘功能修复测试")
    print("=" * 60)
    
    try:
        # 测试显示配置
        test_display_config()
        
        # 测试轮盘功能
        test_disk_fixes()
        
        print("\n🎉 所有测试完成！")
        print("如果轮盘:")
        print("  ✅ 能够置顶显示")
        print("  ✅ 能够在设定时间后自动隐藏") 
        print("  ✅ 切换模式时有视觉效果变化")
        print("那么修复就是成功的！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()