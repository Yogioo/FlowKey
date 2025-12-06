# -*- coding: utf-8 -*-
"""
旋转环形指示器UI组件
使用PIL抗锯齿渲染的旋转环形UI
"""

import tkinter as tk
import math
from PIL import Image, ImageDraw, ImageTk, ImageFont
from ..config.settings import GlobalConfig


class WheelDisk:
    """旋转环形指示器类 - 圆环旋转指向当前模式"""

    MODES = ["浏览模式", "影音模式", "视频模式", "窗口管理"]
    # 简约配色 - 低饱和度的现代色调
    COLORS = [
        "#E8E8E8",  # 浅灰 - 浏览模式
        "#D0D0D0",  # 中灰 - 影音模式
        "#B8B8B8",  # 深灰 - 视频模式
        "#A0A0A0",  # 更深灰 - 窗口管理
    ]
    # 当前模式的高亮色
    ACTIVE_COLOR = "#FFFFFF"  # 纯白
    INACTIVE_COLOR = "#404040"  # 深灰

    # 模式标签的固定角度位置（对齐到每个象限的中心）
    MODE_ANGLES = [45, 135, 225, 315]  # 右上、左上、左下、右下（每个象限中心）

    def __init__(self):
        self.current_mode = 0
        self.root = None
        self.canvas = None
        self.visible = False
        self.hide_timer = None
        self.size = 320
        self.scale = 4
        self.tk_image = None

        # 从配置加载显示参数
        self.display_config = self._load_display_config()

        # 旋转动画相关（现在只有指针旋转）
        self.pointer_angle = 0  # 当前指针角度
        self.target_pointer_angle = 0  # 目标指针角度
        self.rotation_direction = 1  # 旋转方向：1=顺时针，-1=逆时针
        self.is_animating = False
        self.animation_timer = None

    def _load_display_config(self) -> dict:
        """从配置加载显示参数"""
        default_config = {
            'fade_step': 20,
            'hide_delay': 600,
            'rotation_speed': 40,  # 旋转动画速度（度/帧）- 更快
        }

        try:
            config = GlobalConfig.load()
            display_config = config.get('display', {})
            default_config.update(display_config)
        except:
            pass

        return default_config

    def create_window(self):
        """创建圆盘窗口"""
        self.root = tk.Tk()
        self.root.title("模式切换")
        self.root.overrideredirect(True)

        self.root.attributes('-alpha', 1.0)
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.wm_attributes("-topmost", True)

        # 从配置加载窗口设置
        window_config = GlobalConfig.get('window', {})
        self.size = window_config.get('size', 320)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        if window_config.get('center_on_screen', True):
            x = (screen_w - self.size) // 2
            y = (screen_h - self.size) // 2
        else:
            x, y = 100, 100

        self.root.geometry(f"{self.size}x{self.size}+{x}+{y}")

        self.root.config(bg='#1a1a1a')
        self.root.attributes('-transparentcolor', '#1a1a1a')

        self.canvas = tk.Canvas(self.root, width=self.size, height=self.size,
                               bg='#1a1a1a', highlightthickness=0)
        self.canvas.pack()
        self.root.withdraw()

    def _hex_to_rgb(self, hex_color):
        """十六进制颜色转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _interpolate_angle(self, current, target):
        """计算角度插值（处理360度循环）"""
        diff = (target - current) % 360
        if diff > 180:
            diff -= 360
        return diff

    def _animate_rotation(self):
        """执行指针旋转动画（按固定方向旋转）"""
        if not self.is_animating or not self.root:
            return

        # 计算角度差（不使用最短路径，而是按指定方向旋转）
        current = self.pointer_angle
        target = self.target_pointer_angle

        # 按照指定方向计算差值
        # 注意：由于使用标准数学坐标系（y向上），角度增加=逆时针，角度减少=顺时针
        if self.rotation_direction > 0:  # 顺时针（角度减少）
            diff = -((current - target) % 360)
        else:  # 逆时针（角度增加）
            diff = (target - current) % 360

        # 如果差值很小，直接设置为目标值
        if abs(diff) < 1:
            self.pointer_angle = self.target_pointer_angle
            self.is_animating = False
            self.animation_timer = None
            self.draw_disk()
            # 动画完成后重新设置自动隐藏定时器
            self._reset_hide_timer()
            return

        # 渐进式旋转
        speed = self.display_config.get('rotation_speed', 40)
        step = min(speed, abs(diff)) * (1 if diff > 0 else -1)
        self.pointer_angle = (self.pointer_angle + step) % 360

        # 重绘并继续动画
        self.draw_disk()
        self.animation_timer = self.root.after(10, self._animate_rotation)  # ~100fps 更流畅

    def draw_disk(self):
        """绘制旋转环形指示器"""
        if not self.canvas:
            return

        self.canvas.delete("all")

        # 高分辨率画布用于抗锯齿
        big_size = self.size * self.scale
        cx, cy = big_size // 2, big_size // 2

        # 创建背景图像 - 使用与transparentcolor相同的颜色(#1a1a1a)避免抗锯齿边缘伪影
        # 这个深灰色会被tkinter当作透明处理,同时解决了半透明像素的"污渍"问题
        bg_color = (26, 26, 26, 255)  # #1a1a1a with full opacity
        img = Image.new('RGBA', (big_size, big_size), bg_color)
        draw = ImageDraw.Draw(img)

        # 绘制旋转的彩色圆环
        self._draw_rotating_ring(draw, cx, cy, big_size)

        # 绘制中心指针
        self._draw_center_pointer(draw, cx, cy, big_size)

        # 缩放到目标尺寸（抗锯齿）
        img = img.resize((self.size, self.size), Image.Resampling.LANCZOS)

        # 绘制固定的模式标签
        self._draw_mode_labels(img)

        # 转换为Tkinter图像并显示
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(self.size // 2, self.size // 2, image=self.tk_image)

    def _draw_rotating_ring(self, draw, cx, cy, size):
        """绘制简约风格的固定圆环"""
        r_outer = int(size * 0.40)  # 稍微增大外半径
        r_inner = int(size * 0.26)  # 稍微减小内半径，让圆环更宽

        # 固定的4个象限，使用简约配色
        quadrants = [
            (0, 90, 0),      # 右侧 - 浏览模式
            (90, 180, 1),    # 上侧 - 影音模式
            (180, 270, 2),   # 左侧 - 视频模式
            (270, 360, 3),   # 下侧 - 窗口管理
        ]

        for start_angle, end_angle, mode_idx in quadrants:
            # 当前模式用白色，其他用深灰
            if mode_idx == self.current_mode:
                color = self._hex_to_rgb(self.ACTIVE_COLOR)
            else:
                color = self._hex_to_rgb(self.INACTIVE_COLOR)

            # 绘制纯色扇形，不要渐变
            for i in range(start_angle, end_angle, 2):
                self._draw_arc_segment(draw, cx, cy, r_outer, r_inner, i, i + 2, color)

        # 绘制分隔线（细线条）
        separator_width = 2 * self.scale
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            x1 = cx + r_inner * math.cos(rad)
            y1 = cy - r_inner * math.sin(rad)
            x2 = cx + r_outer * math.cos(rad)
            y2 = cy - r_outer * math.sin(rad)
            draw.line([(x1, y1), (x2, y2)], fill=(30, 30, 30, 255), width=separator_width)

    def _draw_arc_segment(self, draw, cx, cy, r_outer, r_inner, start, end, color):
        """绘制一小段圆弧"""
        points = []
        # 外弧
        for angle in range(start, end + 1):
            rad = math.radians(angle)
            x = cx + r_outer * math.cos(rad)
            y = cy - r_outer * math.sin(rad)
            points.append((x, y))
        # 内弧（反向）
        for angle in range(end, start - 1, -1):
            rad = math.radians(angle)
            x = cx + r_inner * math.cos(rad)
            y = cy - r_inner * math.sin(rad)
            points.append((x, y))

        if len(points) > 2:
            draw.polygon(points, fill=color + (255,))

    def _draw_center_pointer(self, draw, cx, cy, size):
        """绘制简约风格的中心指针"""
        # 指针根据当前角度旋转
        rad = math.radians(self.pointer_angle)

        # 简化的指针 - 一条细长的线
        pointer_length = int(size * 0.18)
        pointer_width = 2 * self.scale

        # 指针终点
        end_x = cx + pointer_length * math.cos(rad)
        end_y = cy - pointer_length * math.sin(rad)

        # 绘制细线指针
        draw.line([(cx, cy), (end_x, end_y)],
                 fill=(255, 255, 255, 255), width=pointer_width)

        # 指针末端小圆点
        dot_r = int(size * 0.01)
        draw.ellipse([end_x - dot_r, end_y - dot_r, end_x + dot_r, end_y + dot_r],
                     fill=(255, 255, 255, 255))

        # 中心圆 - 简约风格
        center_r = int(size * 0.06)
        draw.ellipse([cx - center_r, cy - center_r, cx + center_r, cy + center_r],
                     fill=(20, 20, 20, 255), outline=(200, 200, 200, 255),
                     width=2*self.scale)

    def _draw_mode_labels(self, img):
        """绘制固定位置的模式标签"""
        draw = ImageDraw.Draw(img)
        cx, cy = self.size // 2, self.size // 2

        # 加载字体
        try:
            font = ImageFont.truetype("msyh.ttc", 12)
        except:
            font = ImageFont.load_default()

        # 标签半径
        label_radius = self.size * 0.33

        for i, angle in enumerate(self.MODE_ANGLES):
            rad = math.radians(angle)
            tx = cx + label_radius * math.cos(rad)
            ty = cy - label_radius * math.sin(rad)

            # 简约风格 - 当前模式深色文字（白底黑字），其他亮灰色
            if i == self.current_mode:
                text_color = (30, 30, 30, 255)  # 深灰/黑色，在白色背景上清晰可见
            else:
                text_color = (200, 200, 200, 255)  # 亮灰色，在深色背景上清晰

            draw.text((tx, ty), self.MODES[i], font=font,
                     fill=text_color, anchor="mm")

    def show(self):
        """显示圆盘"""
        if self.root:
            self.root.lift()
            self.root.attributes('-topmost', True)

            self.draw_disk()

            if not self.visible:
                self.root.attributes('-alpha', 1.0)
                self.root.deiconify()
                self._reset_hide_timer()
            else:
                self._reset_hide_timer()
            self.visible = True

    def hide(self):
        """隐藏圆盘"""
        if self.root and self.visible:
            self.root.withdraw()
            self.visible = False

    def _reset_hide_timer(self):
        """重置自动隐藏定时器"""
        if self.hide_timer:
            try:
                self.root.after_cancel(self.hide_timer)
                self.hide_timer = None
            except:
                pass

        try:
            delay = self.display_config.get('hide_delay', 600)
            self.hide_timer = self.root.after(delay, self.hide)
        except Exception as e:
            print(f"设置隐藏定时器失败: {e}")

    def _start_rotation_animation(self, target_angle, direction=1):
        """开始指针旋转动画

        Args:
            target_angle: 目标角度
            direction: 旋转方向，1=顺时针，-1=逆时针
        """
        self.target_pointer_angle = target_angle % 360
        self.rotation_direction = direction

        # 取消自动隐藏定时器，避免动画过程中被隐藏
        if self.hide_timer:
            try:
                self.root.after_cancel(self.hide_timer)
                self.hide_timer = None
            except:
                pass

        # 如果已经在动画中，取消旧动画
        if self.animation_timer:
            try:
                self.root.after_cancel(self.animation_timer)
                self.animation_timer = None
            except:
                pass

        self.is_animating = True
        self._animate_rotation()

    def next_mode(self):
        """切换到下一个模式"""
        # 改为逆向切换模式索引，但保持顺时针旋转
        self.current_mode = (self.current_mode - 1) % 4

        # 计算指针目标角度（指针转动，指向当前模式象限中心）
        # 模式0=右上(45度), 模式1=左上(135度), 模式2=左下(225度), 模式3=右下(315度)
        target_angle = 45 + self.current_mode * 90

        # 确保窗口显示
        if not self.visible:
            self.root.attributes('-alpha', 1.0)
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.visible = True

        # 启动旋转动画 - 顺时针旋转（与旋钮方向一致）
        self._start_rotation_animation(target_angle, direction=1)

        print(f"切换到: {self.MODES[self.current_mode]}")

    def prev_mode(self):
        """切换到上一个模式"""
        # 改为正向切换模式索引，但保持逆时针旋转
        self.current_mode = (self.current_mode + 1) % 4

        # 计算指针目标角度（指向象限中心）
        target_angle = 45 + self.current_mode * 90

        # 确保窗口显示
        if not self.visible:
            self.root.attributes('-alpha', 1.0)
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.visible = True

        # 启动旋转动画 - 逆时针旋转（与旋钮方向一致）
        self._start_rotation_animation(target_angle, direction=-1)

        print(f"切换到: {self.MODES[self.current_mode]}")

    def get_current_mode(self):
        return self.current_mode

    def get_display_config(self):
        """获取显示配置副本"""
        return self.display_config.copy()

    def set_display_config(self, config):
        """设置显示配置"""
        if isinstance(config, dict):
            self.display_config.update(config)

            try:
                for key, value in config.items():
                    GlobalConfig.set(f'display.{key}', value)
                GlobalConfig.save()
            except:
                pass
