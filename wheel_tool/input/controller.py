# -*- coding: utf-8 -*-
"""
模式控制器模块
提供模式切换控制逻辑
"""

from typing import Optional, Any


class ModeController:
    """模式控制器"""

    def __init__(self, disk):
        self.disk = disk

    def switch_to_next_mode(self):
        """切换到下一个模式"""
        if hasattr(self.disk, 'next_mode'):
            self.disk.next_mode()

    def switch_to_prev_mode(self):
        """切换到上一个模式"""
        if hasattr(self.disk, 'prev_mode'):
            self.disk.prev_mode()

    def switch_to_mode(self, mode_index: int):
        """切换到指定模式"""
        if hasattr(self.disk, 'current_mode') and 0 <= mode_index < len(self.disk.MODES):
            self.disk.current_mode = mode_index
            if hasattr(self.disk, 'update_display'):
                self.disk.update_display()

    def get_current_mode(self) -> int:
        """获取当前模式索引"""
        return getattr(self.disk, 'current_mode', 0)

    def get_mode_count(self) -> int:
        """获取模式总数"""
        return len(getattr(self.disk, 'MODES', []))

    def is_mode_valid(self, mode_index: int) -> bool:
        """检查模式索引是否有效"""
        return 0 <= mode_index < self.get_mode_count()