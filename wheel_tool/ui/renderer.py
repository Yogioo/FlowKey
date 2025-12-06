# -*- coding: utf-8 -*-
"""
渲染引擎
提供图形渲染和抗锯齿处理功能
"""

import math
from PIL import Image, ImageDraw, ImageFilter
from typing import Tuple, List, Optional


class RenderEngine:
    """渲染管理器"""
    
    def __init__(self, size: int = 320, scale_factor: int = 4):
        self.size = size
        self.scale_factor = scale_factor
        self.antialiasing = Antialiasing()
        self.graphics = Graphics()

    def create_canvas(self, background: str = "transparent") -> Image.Image:
        """创建画布"""
        if background == "transparent":
            return Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
        else:
            return Image.new('RGB', (self.size, self.size), background)

    def render_disk(self, disk_data: dict) -> Image.Image:
        """渲染圆盘"""
        # 创建高分辨率画布用于抗锯齿
        high_res_size = self.size * self.scale_factor
        img = Image.new('RGBA', (high_res_size, high_res_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 渲染各个组件
        self._render_segments(draw, disk_data, high_res_size)
        self._render_separators(draw, disk_data, high_res_size)
        self._render_center(draw, disk_data, high_res_size)
        
        # 应用抗锯齿并缩放到目标尺寸
        final_img = self.antialiasing.apply_antialiasing(img, self.size)
        
        return final_img

    def _render_segments(self, draw: ImageDraw.ImageDraw, data: dict, size: int):
        """渲染扇形段"""
        cx, cy = size // 2, size // 2
        r_outer = int(size * 0.42)
        r_inner = int(size * 0.18)
        
        segments = data.get('segments', [])
        for segment in segments:
            self.graphics.draw_gradient_arc(
                draw, cx, cy, r_outer, r_inner,
                segment['start'], segment['end'],
                segment['colors']
            )

    def _render_separators(self, draw: ImageDraw.ImageDraw, data: dict, size: int):
        """渲染分隔线"""
        cx, cy = size // 2, size // 2
        r_inner = int(size * 0.18)
        r_outer = int(size * 0.42)
        
        angles = data.get('separator_angles', [0, 90, 180, 270])
        rotation = data.get('rotation', 0)
        
        for base_angle in angles:
            angle = (base_angle + rotation) % 360
            rad = math.radians(angle)
            x1 = cx + r_inner * math.cos(rad)
            y1 = cy - r_inner * math.sin(rad)
            x2 = cx + r_outer * math.cos(rad)
            y2 = cy - r_outer * math.sin(rad)
            
            self.graphics.draw_glow_line(draw, x1, y1, x2, y2)

    def _render_center(self, draw: ImageDraw.ImageDraw, data: dict, size: int):
        """渲染中心圆"""
        cx, cy = size // 2, size // 2
        center_r = int(size * 0.12)
        
        # 中心圆主体
        colors = data.get('center_colors', [(100, 100, 100), (150, 150, 150)])
        draw.ellipse([cx - center_r, cy - center_r, cx + center_r, cy + center_r],
                     fill=colors[0], outline=colors[1], width=3)

        # 中心光点
        highlight_r = center_r // 3
        draw.ellipse([cx - highlight_r, cy - highlight_r,
                     cx + highlight_r, cy + highlight_r],
                     fill=(255, 255, 255, 255))


class Antialiasing:
    """抗锯齿处理器"""
    
    def __init__(self):
        self.blur_radius = 0.5
        
    def apply_antialiasing(self, img: Image.Image, target_size: int) -> Image.Image:
        """应用抗锯齿处理"""
        # 使用LANCZOS重采样进行高质量缩放
        resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
        return resized
    
    def apply_gaussian_blur(self, img: Image.Image, radius: float = 1.0) -> Image.Image:
        """应用高斯模糊"""
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    
    def apply_edge_smoothing(self, img: Image.Image) -> Image.Image:
        """边缘平滑处理"""
        # 轻微的模糊来平滑边缘
        return self.apply_gaussian_blur(img, self.blur_radius)


class Graphics:
    """图形绘制工具"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """十六进制颜色转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def draw_gradient_arc(draw: ImageDraw.ImageDraw, cx: int, cy: int, 
                         r_outer: int, r_inner: int, start: int, end: int, 
                         colors: List[str]):
        """绘制渐变扇形"""
        if not colors:
            colors = ["#7c3aed", "#a855f7"]
            
        steps = 10
        for i in range(steps):
            t = i / steps
            color1 = Graphics.hex_to_rgb(colors[0]) if isinstance(colors[0], str) else colors[0]
            color2 = Graphics.hex_to_rgb(colors[1]) if len(colors) > 1 and isinstance(colors[1], str) else colors[1]
            
            # 颜色插值
            color = (
                int(color1[0] * (1-t) + color2[0] * t),
                int(color1[1] * (1-t) + color2[1] * t),
                int(color1[2] * (1-t) + color2[2] * t)
            )
            
            current_r = r_outer - (r_outer - r_inner) * t
            next_r = r_outer - (r_outer - r_inner) * (t + 1/steps)
            
            Graphics.draw_arc_aa(draw, cx, cy, current_r, next_r, start, end, color)

    @staticmethod
    def draw_arc_aa(draw: ImageDraw.ImageDraw, cx: int, cy: int, 
                    r_outer: int, r_inner: int, start: int, end: int, color: Tuple[int, int, int]):
        """绘制抗锯齿扇形（通过多边形近似）"""
        points = []
        # 外弧
        for angle in range(start, min(end + 1, start + 90), 2):
            rad = math.radians(angle)
            x = cx + r_outer * math.cos(rad)
            y = cy - r_outer * math.sin(rad)
            points.append((x, y))
        # 内弧（反向）
        for angle in range(end, max(start - 1, end - 90), -2):
            rad = math.radians(angle)
            x = cx + r_inner * math.cos(rad)
            y = cy - r_inner * math.sin(rad)
            points.append((x, y))

        if len(points) > 2:
            draw.polygon(points, fill=color + (255,))

    @staticmethod
    def draw_glow_line(draw: ImageDraw.ImageDraw, x1: float, y1: float, 
                       x2: float, y2: float, color: Tuple[int, int, int] = (255, 255, 255)):
        """绘制发光线条"""
        base_width = 2
        for i in range(4, 0, -1):
            alpha = 180 + (4-i) * 30
            width = base_width * i
            draw.line([(x1, y1), (x2, y2)], fill=(*color, alpha), width=width)

    @staticmethod
    def draw_glow_ellipse(draw: ImageDraw.ImageDraw, cx: int, cy: int, 
                          radius: int, color: Tuple[int, int, int], alpha_base: int = 120):
        """绘制发光椭圆"""
        layers = [
            (radius + 15, alpha_base + 60),
            (radius + 10, alpha_base + 80),
            (radius + 5, alpha_base + 100),
        ]
        
        for layer_r, alpha in layers:
            draw.ellipse([cx - layer_r, cy - layer_r, cx + layer_r, cy + layer_r],
                        fill=(*color, alpha), outline=None)

    @staticmethod
    def blend_colors(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                    t: float) -> Tuple[int, int, int]:
        """混合两个颜色"""
        return (
            int(color1[0] * (1-t) + color2[0] * t),
            int(color1[1] * (1-t) + color2[1] * t),
            int(color1[2] * (1-t) + color2[2] * t)
        )