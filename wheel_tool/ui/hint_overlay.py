# -*- coding: utf-8 -*-
"""
按键提示悬浮窗组件
在屏幕下方显示透明的按键提示文本
"""

import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFont
from ..config.settings import GlobalConfig


class HintOverlay:
    """按键提示悬浮窗 - 在屏幕下方显示半透明提示"""

    def __init__(self, parent=None):
        """
        初始化提示窗口

        Args:
            parent: 父窗口（必须提供，否则会创建独立窗口）
        """
        self.parent = parent
        self.window = None
        self.canvas = None
        self.tk_image = None
        self.hide_timer = None
        self.visible = False

        # 从配置加载提示显示参数
        self.hint_config = self._load_hint_config()

        # 窗口尺寸
        self.width = self.hint_config.get('width', 400)
        self.height = self.hint_config.get('height', 80)
        self.scale = 2  # 用于抗锯齿渲染

    def _load_hint_config(self) -> dict:
        """从配置加载提示显示参数"""
        default_config = {
            'enabled': True,
            'width': 400,
            'height': 80,
            'alpha': 0.85,
            'display_duration': 1200,  # 显示时长（毫秒）
            'bottom_margin': 100,  # 距离屏幕底部的距离
            'font_size': 24,
            'background_color': '#2a2a2a',
            'text_color': '#ffffff',
            'border_radius': 12,
        }

        try:
            config = GlobalConfig.load()
            hint_config = config.get('hint_overlay', {})
            default_config.update(hint_config)
        except:
            pass

        return default_config

    def create_window(self):
        """创建提示窗口"""
        if self.window:
            return

        # 如果没有父窗口，不创建（避免空白窗口）
        if not self.parent:
            print("警告：HintOverlay 需要父窗口才能正常工作")
            return

        self.window = tk.Toplevel(self.parent)
        self.window.title("按键提示")
        self.window.overrideredirect(True)

        # 设置透明度
        alpha = self.hint_config.get('alpha', 0.85)
        self.window.attributes('-alpha', alpha)
        self.window.attributes('-topmost', True)

        # 计算窗口位置（屏幕下方居中）
        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        bottom_margin = self.hint_config.get('bottom_margin', 100)

        x = (screen_w - self.width) // 2
        y = screen_h - self.height - bottom_margin

        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # 设置透明色背景
        self.window.config(bg='#1a1a1a')
        self.window.attributes('-transparentcolor', '#1a1a1a')

        # 创建画布
        self.canvas = tk.Canvas(
            self.window,
            width=self.width,
            height=self.height,
            bg='#1a1a1a',
            highlightthickness=0
        )
        self.canvas.pack()

        # 立即隐藏窗口，避免显示空白窗口
        self.window.withdraw()
        self.visible = False

    def _hex_to_rgb(self, hex_color):
        """十六进制颜色转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _draw_rounded_rectangle(self, draw, xy, radius, fill):
        """绘制圆角矩形"""
        x1, y1, x2, y2 = xy

        # 绘制主体矩形
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)

        # 绘制四个圆角
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)

    def show(self, hint_text: str):
        """
        显示提示文本

        Args:
            hint_text: 要显示的提示文本
        """
        if not self.hint_config.get('enabled', True):
            return

        # 确保窗口已创建
        if not self.window:
            self.create_window()

        # 取消之前的隐藏定时器
        if self.hide_timer:
            try:
                self.window.after_cancel(self.hide_timer)
                self.hide_timer = None
            except:
                pass

        # 绘制提示内容
        self._draw_hint(hint_text)

        # 显示窗口
        if not self.visible:
            self.window.deiconify()
            self.window.lift()
            self.window.attributes('-topmost', True)
            self.visible = True

        # 设置自动隐藏定时器
        duration = self.hint_config.get('display_duration', 1200)
        self.hide_timer = self.window.after(duration, self.hide)

    def _draw_hint(self, hint_text: str):
        """绘制提示内容"""
        if not self.canvas:
            return

        self.canvas.delete("all")

        # 高分辨率画布用于抗锯齿
        big_width = self.width * self.scale
        big_height = self.height * self.scale

        # 创建透明背景图像
        img = Image.new('RGBA', (big_width, big_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 获取颜色配置
        bg_color = self._hex_to_rgb(self.hint_config.get('background_color', '#2a2a2a'))
        text_color = self._hex_to_rgb(self.hint_config.get('text_color', '#ffffff'))
        border_radius = self.hint_config.get('border_radius', 12) * self.scale

        # 绘制圆角矩形背景
        padding = 10 * self.scale
        self._draw_rounded_rectangle(
            draw,
            [padding, padding, big_width - padding, big_height - padding],
            border_radius,
            bg_color + (200,)  # 添加 alpha 通道
        )

        # 加载字体
        font_size = self.hint_config.get('font_size', 24) * self.scale
        try:
            font = ImageFont.truetype("msyh.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

        # 绘制文本
        cx = big_width // 2
        cy = big_height // 2
        draw.text(
            (cx, cy),
            hint_text,
            font=font,
            fill=text_color + (255,),
            anchor="mm"
        )

        # 缩放到目标尺寸（抗锯齿）
        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)

        # 转换为 Tkinter 图像并显示
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(self.width // 2, self.height // 2, image=self.tk_image)

    def hide(self):
        """隐藏提示窗口"""
        if self.window and self.visible:
            self.window.withdraw()
            self.visible = False

            # 取消定时器
            if self.hide_timer:
                try:
                    self.window.after_cancel(self.hide_timer)
                    self.hide_timer = None
                except:
                    pass

    def update_config(self, new_config: dict):
        """更新配置并重新创建窗口"""
        # 更新配置
        self.hint_config.update(new_config)

        # 更新尺寸
        self.width = self.hint_config.get('width', 400)
        self.height = self.hint_config.get('height', 80)

        # 如果窗口已存在，销毁并重新创建
        if self.window:
            try:
                self.window.destroy()
            except:
                pass
            self.window = None
            self.canvas = None
            self.tk_image = None

        # 重新创建窗口
        if self.parent:
            self.create_window()

    def destroy(self):
        """销毁窗口"""
        if self.hide_timer:
            try:
                self.window.after_cancel(self.hide_timer)
                self.hide_timer = None
            except:
                pass

        if self.window:
            try:
                self.window.destroy()
            except:
                pass
            self.window = None
            self.canvas = None
            self.tk_image = None
            self.visible = False
