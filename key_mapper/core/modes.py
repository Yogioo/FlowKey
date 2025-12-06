# -*- coding: utf-8 -*-
"""
具体模式实现
包含各种模式的定义和默认配置
"""

from .models import BaseMode


class BrowseMode(BaseMode):
    """浏览模式"""

    def __init__(self):
        super().__init__("浏览模式", "#7c3aed")  # 统一紫色

    def get_default_mappings(self) -> list:
        return [
            ("j", "down"),
            ("k", "up"),
            ("h", "left"),
            ("l", "right"),
        ]


class MediaMode(BaseMode):
    """影音模式"""

    def __init__(self):
        super().__init__("影音模式", "#7c3aed")  # 统一紫色

    def get_default_mappings(self) -> list:
        return [
            ("j", "down"),
            ("k", "up"),
        ]


class VideoMode(BaseMode):
    """视频模式"""

    def __init__(self):
        super().__init__("视频模式", "#7c3aed")  # 统一紫色

    def get_default_mappings(self) -> list:
        return [
            ("h", "left"),
            ("l", "right"),
        ]


class WindowMode(BaseMode):
    """窗口管理模式"""

    def __init__(self):
        super().__init__("窗口管理", "#7c3aed")  # 统一紫色

    def get_default_mappings(self) -> list:
        # 返回空列表，在 load_defaults 中手动设置高级映射
        return []

    def load_defaults(self):
        """加载默认映射 - 重写以支持高级映射类型"""
        from .models import KeyMapping
        self.clear_mappings()

        # f24 右旋 -> 下一个窗口
        self.mappings["f24"] = KeyMapping(
            source_key="f24",
            target_key="next",
            block=True,
            hint="下一个窗口",
            action_type="window_cycle"
        )

        # f23 左旋 -> 上一个窗口
        self.mappings["f23"] = KeyMapping(
            source_key="f23",
            target_key="prev",
            block=True,
            hint="上一个窗口",
            action_type="window_cycle"
        )


class CustomMode(BaseMode):
    """自定义模式 - 用户可以自由配置"""

    def __init__(self, name="自定义模式", color="#7c3aed"):
        super().__init__(name, color)

    def get_default_mappings(self) -> list:
        return []  # 自定义模式默认为空