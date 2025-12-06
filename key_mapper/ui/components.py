# -*- coding: utf-8 -*-
"""
UI组件基类和通用工具
提供统一的UI组件基础功能
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional


class BasePanel:
    """面板基类 - 提供通用的UI面板功能"""
    
    # 默认颜色主题
    DEFAULT_COLORS = {
        "bg": "#1e1e2e",           # 深色背景
        "bg_secondary": "#2a2a3e", # 次级背景
        "accent": "#7c3aed",       # 主题紫色
        "accent_hover": "#8b5cf6", # 悬停紫色
        "text": "#e2e8f0",         # 主文字
        "text_dim": "#94a3b8",     # 次要文字
        "border": "#3f3f5a",       # 边框
        "success": "#22c55e",      # 成功绿
        "warning": "#f59e0b",      # 警告黄
        "danger": "#ef4444",       # 危险红
    }
    
    def __init__(self, parent=None, colors: Optional[Dict[str, str]] = None):
        self.parent = parent
        self.window = None
        self.colors = colors or self.DEFAULT_COLORS.copy()
        
    def setup_styles(self):
        """配置ttk样式"""
        style = ttk.Style()
        style.theme_use("clam")

        # 配置Treeview样式
        style.configure("Custom.Treeview",
                        background=self.colors["bg_secondary"],
                        foreground=self.colors["text"],
                        fieldbackground=self.colors["bg_secondary"],
                        borderwidth=0,
                        rowheight=32)
        style.configure("Custom.Treeview.Heading",
                        background=self.colors["bg"],
                        foreground=self.colors["text"],
                        borderwidth=0,
                        font=("Microsoft YaHei UI", 9, "bold"))

        # 配置滚动条样式
        style.configure("Custom.Vertical.TScrollbar",
                        background=self.colors["bg"],
                        troughcolor=self.colors["bg_secondary"],
                        bordercolor=self.colors["border"],
                        lightcolor=self.colors["accent"],
                        darkcolor=self.colors["accent"],
                        arrowcolor=self.colors["text_dim"],
                        width=12,
                        relief="flat")

    def create_btn(self, parent, text, command, bg=None, fg=None, width=None):
        """创建统一风格按钮"""
        btn = tk.Button(parent, text=text, font=("Microsoft YaHei UI", 9),
                        bg=bg or self.colors["accent"],
                        fg=fg or "#ffffff",
                        activebackground=self.colors["accent_hover"],
                        bd=0, padx=12, pady=6, cursor="hand2",
                        command=command)
        if width:
            btn.configure(width=width)
        return btn

    def create_frame(self, parent, highlight=True):
        """创建标准样式的框架"""
        frame = tk.Frame(parent, bg=self.colors["bg_secondary"])
        if highlight:
            frame.configure(highlightbackground=self.colors["border"], highlightthickness=1)
        return frame

    def create_label(self, parent, text, font_size=9, color_key="text", bold=False):
        """创建统一风格标签"""
        font_weight = "bold" if bold else "normal"
        font = ("Microsoft YaHei UI", font_size, font_weight)
        fg = self.colors.get(color_key, self.colors["text"])
        
        label = tk.Label(parent, text=text, font=font,
                        bg=self.colors["bg_secondary"], fg=fg)
        return label

    def create_entry(self, parent, width=15, font_family="Consolas", font_size=11, textvariable=None):
        """创建统一风格输入框"""
        kwargs = {
            'width': width,
            'font': (font_family, font_size),
            'bg': self.colors["bg"],
            'fg': self.colors["text"],
            'insertbackground': self.colors["accent"],
            'bd': 0,
            'highlightbackground': self.colors["border"],
            'highlightthickness': 1,
            'highlightcolor': self.colors["accent"]
        }

        if textvariable:
            kwargs['textvariable'] = textvariable

        entry = tk.Entry(parent, **kwargs)

        # 添加focus效果
        entry.bind("<FocusIn>", lambda e: self._on_entry_focus_in(entry))
        entry.bind("<FocusOut>", lambda e: self._on_entry_focus_out(entry))

        return entry

    def _on_entry_focus_in(self, entry):
        """输入框获得焦点时高亮"""
        entry.configure(highlightbackground=self.colors["accent"], highlightthickness=2)

    def _on_entry_focus_out(self, entry):
        """输入框失去焦点时恢复"""
        entry.configure(highlightbackground=self.colors["border"], highlightthickness=1)

    def _adjust_brightness(self, hex_color: str, factor: float) -> str:
        """调整颜色的亮度"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"


class UIHelper:
    """UI工具函数类"""
    
    @staticmethod
    def center_window(window: tk.Tk):
        """窗口居中"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def create_draggable_titlebar(window: tk.Tk, title_bar: tk.Frame):
        """创建可拖拽的标题栏"""
        def start_move(event):
            window.is_dragging = True
            window.drag_start_x = event.x_root - window.winfo_x()
            window.drag_start_y = event.y_root - window.winfo_y()

        def on_move(event):
            if hasattr(window, 'is_dragging') and window.is_dragging:
                x = event.x_root - window.drag_start_x
                y = event.y_root - window.drag_start_y
                
                # 确保窗口不会拖到屏幕外
                screen_width = window.winfo_screenwidth()
                screen_height = window.winfo_screenheight()
                window_width = window.winfo_width()
                window_height = window.winfo_height()
                
                x = max(0, min(x, screen_width - window_width))
                y = max(0, min(y, screen_height - window_height))
                
                window.geometry(f"+{x}+{y}")

        def stop_move(event):
            window.is_dragging = False

        # 绑定事件
        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", on_move)
        title_bar.bind("<ButtonRelease-1>", stop_move)

    @staticmethod
    def setup_window_controls(window: tk.Tk, title_bar: tk.Frame, 
                           on_close=None, on_maximize=None):
        """设置窗口控制按钮"""
        btn_frame = tk.Frame(title_bar, bg="#2a2a3e")
        btn_frame.pack(side="right", padx=5, pady=5)

        # 关闭按钮
        close_btn = tk.Label(btn_frame, text="✕", font=("Microsoft YaHei UI", 10, "bold"),
                           bg="#2a2a3e", fg="#e2e8f0",
                           cursor="hand2", padx=8, pady=2)
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: (on_close() if on_close else window.destroy()))
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#ff4757", fg="white"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg="#2a2a3e", fg="#e2e8f0"))

        # 最大化按钮
        maximize_btn = tk.Label(btn_frame, text="⬜", font=("Microsoft YaHei UI", 10, "bold"),
                               bg="#2a2a3e", fg="#e2e8f0",
                               cursor="hand2", padx=8, pady=2)
        maximize_btn.pack(side="right", padx=(0, 2))
        
        def toggle_maximize(event):
            if on_maximize:
                on_maximize()
                
        maximize_btn.bind("<Button-1>", toggle_maximize)
        maximize_btn.bind("<Enter>", lambda e: maximize_btn.config(bg="#7c3aed", fg="white"))
        maximize_btn.bind("<Leave>", lambda e: maximize_btn.config(bg="#2a2a3e", fg="#e2e8f0"))

        return close_btn, maximize_btn

    @staticmethod
    def create_tab_switcher(parent: tk.Frame, tabs: list, switch_callback):
        """创建选项卡切换器"""
        tab_frame = tk.Frame(parent, bg="#2a2a3e",
                            highlightbackground="#3f3f5a", highlightthickness=1)
        tab_frame.pack(fill="x", pady=(0, 10))

        tab_inner = tk.Frame(tab_frame, bg="#2a2a3e")
        tab_inner.pack(fill="x", padx=15, pady=10)

        buttons = {}
        for tab_id, tab_text in tabs:
            btn = tk.Button(tab_inner, text=tab_text, font=("Microsoft YaHei UI", 9),
                          bg="#2a2a3e", fg="#94a3b8",
                          activebackground="#1e1e2e", activeforeground="#7c3aed",
                          bd=0, padx=15, pady=6, cursor="hand2",
                          command=lambda t=tab_id: switch_callback(t))
            btn.pack(side="left", padx=2)
            buttons[tab_id] = btn

        return tab_frame, buttons