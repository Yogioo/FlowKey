# -*- coding: utf-8 -*-
"""
按键映射配置面板
提供按键映射的添加、编辑、删除功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from ..core.manager import ModeManager
from .components import BasePanel, UIHelper


class MappingPanel(BasePanel):
    """映射配置面板"""

    def __init__(self, mode_manager: ModeManager):
        super().__init__()
        self.manager = mode_manager
        self.window = None
        self.recording_entry = None
        self.editing_source = None  # 正在编辑的源键
        self.mode_var = None
        self.enabled_var = None
        self.enabled_btn = None
        self.mode_menu_btn = None
        self.mode_menu = None
        self.tree = None
        self.add_btn = None
        self.cancel_btn = None
        self.edit_title = None
        self.source_entry = None
        self.target_entry = None
        self.hint_entry = None
        self.block_var = None
        self.block_btn = None
        self.action_type_var = None
        self.action_type_menu = None

        # 动作类型映射(在__init__中初始化,供其他方法使用)
        action_types = [
            ("keyboard", "⌨ 键盘按键"),
            ("mouse_scroll", "🖱 鼠标滚轮"),
            ("mouse_click", "🖱 鼠标点击"),
            ("window_cycle", "🪟 窗口切换"),
            ("command", "⚙ 系统命令")
        ]
        self.action_type_display_map = {label: code for code, label in action_types}
        self.action_type_code_map = {code: label for code, label in action_types}

        # 目标键的不同输入控件
        self.target_keyboard_frame = None  # keyboard: 文本框+录制按钮
        self.target_keyboard_entry = None
        self.target_keyboard_record_btn = None

        self.target_mouse_scroll_frame = None  # mouse_scroll: 方向+数值
        self.target_scroll_direction_var = None
        self.target_scroll_direction_menu = None
        self.target_scroll_amount_entry = None

        self.target_mouse_click_frame = None  # mouse_click: 按钮选择
        self.target_mouse_click_var = None
        self.target_mouse_click_menu = None

        self.target_window_cycle_frame = None  # window_cycle: 方向选择
        self.target_window_cycle_var = None
        self.target_window_cycle_menu = None

        self.target_command_frame = None  # command: 文本框
        self.target_command_entry = None

        # 标签页相关
        self.current_tab = "mappings"  # 当前激活的标签页
        self.tab_frames = {}  # 存储各个标签页的框架
        self.tab_buttons = {}  # 存储标签页按钮

    def show(self):
        """显示设置窗口"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel()
        self.window.title("⌨ 快捷键映射设置")
        self.window.configure(bg=self.colors["bg"])

        # 设置窗口大小和居中
        self.window.geometry("700x950")
        self.window.minsize(650, 900)
        self.window.maxsize(1200, 1600)
        
        UIHelper.center_window(self.window)
        
        # 移除系统边框
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', False)

        self.setup_styles()

        # 自定义标题栏
        title_bar = tk.Frame(self.window, bg=self.colors["bg_secondary"], height=35)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        title_content = tk.Frame(title_bar, bg=self.colors["bg_secondary"])
        title_content.pack(fill="x", expand=True)

        # 标题文字
        title_label = tk.Label(title_content, text="⌨ 快捷键映射设置",
                              font=("Microsoft YaHei UI", 9, "bold"),
                              bg=self.colors["bg_secondary"], fg=self.colors["text"])
        title_label.pack(side="left", padx=15, pady=8)

        # 窗口控制按钮
        close_btn, maximize_btn = UIHelper.setup_window_controls(
            self.window, title_content, 
            on_close=lambda: self.window.destroy(),
            on_maximize=self._toggle_maximize
        )

        # 设置拖拽功能
        UIHelper.create_draggable_titlebar(self.window, title_bar)
        UIHelper.create_draggable_titlebar(self.window, title_content)

        # 添加窗口边缘调整大小
        self._setup_resize_handles()

        # 主容器
        main_frame = tk.Frame(self.window, bg=self.colors["bg"])
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # 创建主要内容
        self._create_content(main_frame)

    def _on_action_type_changed(self, event=None):
        """动作类型变化时切换目标输入控件"""
        selected = self.action_type_menu.get()

        # 隐藏所有目标输入控件
        if self.target_keyboard_frame:
            self.target_keyboard_frame.pack_forget()
        if self.target_mouse_scroll_frame:
            self.target_mouse_scroll_frame.pack_forget()
        if self.target_mouse_click_frame:
            self.target_mouse_click_frame.pack_forget()
        if self.target_window_cycle_frame:
            self.target_window_cycle_frame.pack_forget()
        if self.target_command_frame:
            self.target_command_frame.pack_forget()

        # 根据类型显示对应的控件
        if selected == "⌨ 键盘按键":
            if self.target_keyboard_frame:
                self.target_keyboard_frame.pack(fill="x", pady=(8, 5))
        elif selected == "🖱 鼠标滚轮":
            if self.target_mouse_scroll_frame:
                self.target_mouse_scroll_frame.pack(fill="x", pady=(8, 5))
        elif selected == "🖱 鼠标点击":
            if self.target_mouse_click_frame:
                self.target_mouse_click_frame.pack(fill="x", pady=(8, 5))
        elif selected == "🪟 窗口切换":
            if self.target_window_cycle_frame:
                self.target_window_cycle_frame.pack(fill="x", pady=(8, 5))
        elif selected == "⚙ 系统命令":
            if self.target_command_frame:
                self.target_command_frame.pack(fill="x", pady=(8, 5))

    def _toggle_maximize(self):
        """切换最大化状态"""
        if hasattr(self.window, 'maximized') and self.window.maximized:
            # 还原
            if hasattr(self.window, 'pre_maximize_geometry'):
                self.window.geometry(self.window.pre_maximize_geometry)
            self.window.state('normal')
            self.window.maximized = False
        else:
            # 最大化
            self.window.pre_maximize_geometry = self.window.geometry()
            self.window.state('zoomed')
            self.window.maximized = True

    def _setup_resize_handles(self):
        """设置窗口边缘调整大小"""
        border_width = 5

        # 创建四条边的拖拽区域
        edges = [
            ("top", 0, 0, "relwidth", 1, border_width, "top_side"),
            ("bottom", 0, "rely", "relwidth", 1, border_width, "bottom_side"),
            ("left", 0, 0, 1, "relheight", border_width, "left_side"),
            ("right", "relx", 0, border_width, "relheight", border_width, "right_side"),
        ]

        for edge_name, x, y, width, height, size, cursor in edges:
            frame = tk.Frame(self.window, bg=self.colors["border"],
                           height=size if height == border_width else None,
                           width=size if width == border_width else None,
                           cursor=cursor)

            if edge_name == "top":
                frame.place(x=0, y=0, relwidth=1, height=size)
            elif edge_name == "bottom":
                frame.place(x=0, rely=1, relwidth=1, height=size, anchor="sw")
            elif edge_name == "left":
                frame.place(x=0, y=0, relheight=1, width=size)
            elif edge_name == "right":
                frame.place(relx=1, y=0, relheight=1, width=size, anchor="ne")

            # 绑定鼠标事件
            self._bind_resize_events(frame, edge_name)

        # 创建四个角的拖拽区域（支持双向调整）
        corner_size = 10
        corners = [
            ("top_left", 0, 0, corner_size, corner_size, "top_left_corner"),
            ("top_right", "relx", 0, corner_size, corner_size, "top_right_corner"),
            ("bottom_left", 0, "rely", corner_size, corner_size, "bottom_left_corner"),
            ("bottom_right", "relx", "rely", corner_size, corner_size, "bottom_right_corner"),
        ]

        for corner_name, x, y, width, height, cursor in corners:
            frame = tk.Frame(self.window, bg=self.colors["border"],
                           width=width, height=height, cursor=cursor)

            if corner_name == "top_left":
                frame.place(x=0, y=0)
            elif corner_name == "top_right":
                frame.place(relx=1, y=0, anchor="ne")
            elif corner_name == "bottom_left":
                frame.place(x=0, rely=1, anchor="sw")
            elif corner_name == "bottom_right":
                frame.place(relx=1, rely=1, anchor="se")

            # 绑定鼠标事件
            self._bind_resize_events(frame, corner_name)

    def _bind_resize_events(self, widget, edge_type):
        """绑定调整大小的鼠标事件"""
        def on_press(event):
            widget._drag_start_x = event.x_root
            widget._drag_start_y = event.y_root
            widget._drag_start_geometry = self.window.winfo_geometry()

        def on_motion(event):
            if not hasattr(widget, '_drag_start_x'):
                return

            # 解析当前窗口几何信息
            geom = widget._drag_start_geometry
            # 格式: 宽x高+x+y
            size_pos = geom.split('+')
            size = size_pos[0].split('x')
            width, height = int(size[0]), int(size[1])
            x, y = int(size_pos[1]), int(size_pos[2])

            dx = event.x_root - widget._drag_start_x
            dy = event.y_root - widget._drag_start_y

            new_width = width
            new_height = height
            new_x = x
            new_y = y

            # 根据边缘类型调整尺寸
            if 'right' in edge_type:
                new_width = max(self.window.minsize()[0], width + dx)
            if 'left' in edge_type:
                new_width = max(self.window.minsize()[0], width - dx)
                if new_width != width - dx:  # 已达到最小宽度
                    dx = width - new_width
                new_x = x + dx

            if 'bottom' in edge_type:
                new_height = max(self.window.minsize()[1], height + dy)
            if 'top' in edge_type:
                new_height = max(self.window.minsize()[1], height - dy)
                if new_height != height - dy:  # 已达到最小高度
                    dy = height - new_height
                new_y = y + dy

            # 应用新的几何信息
            self.window.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")

        def on_release(event):
            if hasattr(widget, '_drag_start_x'):
                delattr(widget, '_drag_start_x')
                delattr(widget, '_drag_start_y')
                delattr(widget, '_drag_start_geometry')

        widget.bind("<ButtonPress-1>", on_press)
        widget.bind("<B1-Motion>", on_motion)
        widget.bind("<ButtonRelease-1>", on_release)

    def _create_content(self, parent):
        """创建主要内容"""
        # 创建标签页切换器
        tabs = [("mappings", "⌨ 按键映射"), ("advanced", "⚙ 高级设置")]
        _, self.tab_buttons = UIHelper.create_tab_switcher(parent, tabs, self._switch_tab)

        # 创建容器用于存放标签页内容
        self.tab_container = tk.Frame(parent, bg=self.colors["bg"])
        self.tab_container.pack(fill="both", expand=True)

        # 创建各个标签页的内容
        self._create_mappings_tab()
        self._create_advanced_tab()

        # 激活第一个标签页
        self._switch_tab("mappings")

    def _switch_tab(self, tab_id):
        """切换标签页"""
        # 隐藏所有标签页
        for frame in self.tab_frames.values():
            frame.pack_forget()

        # 显示选中的标签页
        if tab_id in self.tab_frames:
            self.tab_frames[tab_id].pack(fill="both", expand=True)
            self.current_tab = tab_id

        # 更新按钮样式
        for btn_id, btn in self.tab_buttons.items():
            if btn_id == tab_id:
                btn.configure(bg=self.colors["accent"], fg="#ffffff", font=("Microsoft YaHei UI", 9, "bold"))
            else:
                btn.configure(bg=self.colors["bg_secondary"], fg=self.colors["text_dim"], font=("Microsoft YaHei UI", 9))

    def _create_mappings_tab(self):
        """创建按键映射标签页"""
        frame = tk.Frame(self.tab_container, bg=self.colors["bg"])
        self.tab_frames["mappings"] = frame

        # 头部：模式选择和启用开关
        header_frame = self.create_frame(frame)
        header_frame.pack(fill="x", pady=(0, 10))

        header_inner = tk.Frame(header_frame, bg=self.colors["bg_secondary"])
        header_inner.pack(fill="x", padx=15, pady=12)

        self._create_header_controls(header_inner)

        # 中部：映射列表
        list_frame = self.create_frame(frame)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        self._create_mapping_list(list_frame)

        # 底部：编辑区
        edit_frame = self.create_frame(frame)
        edit_frame.pack(fill="x", pady=(0, 10))

        self._create_edit_section(edit_frame)

        # 操作按钮区
        self._create_action_buttons(frame)

    def _create_advanced_tab(self):
        """创建高级设置标签页"""
        frame = tk.Frame(self.tab_container, bg=self.colors["bg"])
        self.tab_frames["advanced"] = frame

        # 高级设置区
        advanced_frame = self.create_frame(frame)
        advanced_frame.pack(fill="both", expand=True, pady=(0, 10))

        self._create_advanced_settings(advanced_frame)

        # 按钮区
        btn_frame = tk.Frame(frame, bg=self.colors["bg"])
        btn_frame.pack(fill="x")

        # 左侧：测试预览按钮
        self.create_btn(btn_frame, "🔍 测试预览", self._preview_hint,
                       bg=self.colors["accent"], fg="#fff").pack(side="left")

        # 右侧：保存按钮
        self.create_btn(btn_frame, "💾 保存配置", self._save,
                       bg=self.colors["success"], fg="#fff").pack(side="right")

    def _create_header_controls(self, parent):
        """创建头部控制区"""
        # 当前模式标签
        self.create_label(parent, "当前模式", 9, "text_dim").pack(side="left")

        # 模式选择下拉菜单
        mode_names = [m.name for m in self.manager.modes]
        self.mode_var = tk.StringVar(value=mode_names[0])

        self.mode_menu_btn = self._create_menu_button(parent, mode_names[0])
        self.mode_menu_btn.pack(side="left", padx=(10, 20))

        # 下拉菜单
        self.mode_menu = tk.Menu(self.window, tearoff=0,
                                 bg=self.colors["bg_secondary"],
                                 fg=self.colors["text"],
                                 bd=0,
                                 activebackground=self.colors["accent"],
                                 activeforeground="#ffffff",
                                 font=("Microsoft YaHei UI", 10))

        for mode_name in mode_names:
            self.mode_menu.add_command(label=mode_name,
                                       command=lambda n=mode_name: self._select_mode(n))

        # 启用开关
        self.enabled_var = tk.BooleanVar(value=True)
        self.enabled_btn = tk.Button(parent, text="✓ 已启用", font=("Microsoft YaHei UI", 9),
                                     bg=self.colors["success"], fg="#ffffff",
                                     activebackground=self.colors["success"],
                                     bd=0, padx=12, pady=4, cursor="hand2",
                                     command=self._toggle_enabled)
        self.enabled_btn.pack(side="right")

    def _create_mapping_list(self, parent):
        """创建映射列表"""
        list_header = tk.Frame(parent, bg=self.colors["bg_secondary"])
        list_header.pack(fill="x", padx=15, pady=(12, 8))

        self.create_label(list_header, "按键映射列表", 10, "text", bold=True).pack(side="left")
        self.create_label(list_header, "双击编辑", 8, "text_dim").pack(side="right")

        # 表格容器
        tree_container = tk.Frame(parent, bg=self.colors["bg_secondary"])
        tree_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 滚动条容器
        self.scroll_frame = tk.Frame(tree_container, bg=self.colors["border"], width=12)
        # 默认不显示，等内容加载后再判断

        self.scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical",
                                 style="Custom.Vertical.TScrollbar")
        self.scrollbar.pack(fill="both", expand=True, padx=1, pady=1)

        # 表格
        table_frame = tk.Frame(tree_container, bg=self.colors["bg_secondary"])
        table_frame.pack(side="left", fill="both", expand=True)

        columns = ("source", "target", "block", "hint")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                 style="Custom.Treeview", selectmode="browse")

        # 设置列标题
        self.tree.heading("source", text="源按键")
        self.tree.heading("target", text="目标按键")
        self.tree.heading("block", text="屏蔽")
        self.tree.heading("hint", text="提示文本")

        # 设置列宽
        self.tree.column("source", width=80, anchor="center")
        self.tree.column("target", width=100, anchor="center")
        self.tree.column("block", width=50, anchor="center")
        self.tree.column("hint", width=200, minwidth=150)

        # 配置滚动条，并添加自动显示/隐藏逻辑
        self.tree.configure(yscrollcommand=self._on_scroll)
        self.scrollbar.configure(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)

        # 双击编辑
        self.tree.bind("<Double-1>", self._on_double_click)

        # 刷新列表
        self._refresh_list()

    def _create_edit_section(self, parent):
        """创建编辑区域"""
        edit_inner = tk.Frame(parent, bg=self.colors["bg_secondary"])
        edit_inner.pack(fill="x", padx=15, pady=12)

        # 编辑模式标题
        self.edit_title = self.create_label(edit_inner, "添加新映射", 9, "accent", bold=True)
        self.edit_title.pack(anchor="w")

        # 第零行：动作类型选择
        row0 = tk.Frame(edit_inner, bg=self.colors["bg_secondary"])
        row0.pack(fill="x", pady=(8, 5))

        self.create_label(row0, "动作类型:", 9, "text_dim").pack(side="left")

        # 动作类型下拉菜单(使用已经在__init__中定义的映射)
        self.action_type_var = tk.StringVar(value="keyboard")

        # 使用 ttk.Combobox 创建下拉菜单
        self.action_type_menu = ttk.Combobox(
            row0,
            textvariable=self.action_type_var,
            values=list(self.action_type_display_map.keys()),
            state="readonly",
            width=15,
            font=("Microsoft YaHei UI", 9)
        )

        self.action_type_menu.current(0)  # 默认选择第一项
        self.action_type_menu.pack(side="left", padx=(5, 10))
        self.action_type_menu.bind("<<ComboboxSelected>>", self._on_action_type_changed)

        # 第一行：源键输入
        row1 = tk.Frame(edit_inner, bg=self.colors["bg_secondary"])
        row1.pack(fill="x", pady=(8, 5))

        self.create_label(row1, "源键:", 9, "text_dim").pack(side="left")
        self.source_entry = self.create_entry(row1, width=15)
        self.source_entry.pack(side="left", padx=(5, 3), ipady=4)

        self.create_btn(row1, "录制", lambda: self._start_record(self.source_entry),
                       bg=self.colors["border"], width=4).pack(side="left")

        # 屏蔽选项
        self.block_var = tk.BooleanVar(value=True)
        self.block_btn = tk.Button(row1, text="☑ 屏蔽源键", font=("Microsoft YaHei UI", 8),
                                   bg=self.colors["accent"], fg="#ffffff",
                                   activebackground=self.colors["accent_hover"],
                                   bd=0, padx=8, pady=2, cursor="hand2",
                                   command=self._toggle_block)
        self.block_btn.pack(side="right")

        # 第二行：目标输入区域容器（动态切换）
        row2_container = tk.Frame(edit_inner, bg=self.colors["bg_secondary"])
        row2_container.pack(fill="x", pady=5)

        # === keyboard: 文本框 + 录制按钮 ===
        self.target_keyboard_frame = tk.Frame(row2_container, bg=self.colors["bg_secondary"])

        self.create_label(self.target_keyboard_frame, "目标键:", 9, "text_dim").pack(side="left")
        self.target_keyboard_entry = self.create_entry(self.target_keyboard_frame, width=20)
        self.target_keyboard_entry.pack(side="left", padx=(5, 3), ipady=4)
        self.create_btn(self.target_keyboard_frame, "录制",
                       lambda: self._start_record(self.target_keyboard_entry),
                       bg=self.colors["border"], width=4).pack(side="left")

        # === mouse_scroll: 方向下拉 + 数值输入 ===
        self.target_mouse_scroll_frame = tk.Frame(row2_container, bg=self.colors["bg_secondary"])

        self.create_label(self.target_mouse_scroll_frame, "滚动方向:", 9, "text_dim").pack(side="left")
        self.target_scroll_direction_var = tk.StringVar(value="down")
        self.target_scroll_direction_menu = ttk.Combobox(
            self.target_mouse_scroll_frame,
            textvariable=self.target_scroll_direction_var,
            values=["down", "up"],
            state="readonly",
            width=8,
            font=("Microsoft YaHei UI", 9)
        )
        self.target_scroll_direction_menu.pack(side="left", padx=(5, 15))

        self.create_label(self.target_mouse_scroll_frame, "滚动量:", 9, "text_dim").pack(side="left")
        self.target_scroll_amount_entry = self.create_entry(self.target_mouse_scroll_frame, width=8)
        self.target_scroll_amount_entry.insert(0, "1")
        self.target_scroll_amount_entry.pack(side="left", padx=(5, 0), ipady=4)

        # === mouse_click: 按钮选择 ===
        self.target_mouse_click_frame = tk.Frame(row2_container, bg=self.colors["bg_secondary"])

        self.create_label(self.target_mouse_click_frame, "鼠标按钮:", 9, "text_dim").pack(side="left")
        self.target_mouse_click_var = tk.StringVar(value="left")
        self.target_mouse_click_menu = ttk.Combobox(
            self.target_mouse_click_frame,
            textvariable=self.target_mouse_click_var,
            values=["left", "right", "middle"],
            state="readonly",
            width=12,
            font=("Microsoft YaHei UI", 9)
        )
        self.target_mouse_click_menu.pack(side="left", padx=(5, 0))

        # === window_cycle: 方向选择 ===
        self.target_window_cycle_frame = tk.Frame(row2_container, bg=self.colors["bg_secondary"])

        self.create_label(self.target_window_cycle_frame, "切换方向:", 9, "text_dim").pack(side="left")
        self.target_window_cycle_var = tk.StringVar(value="next")
        self.target_window_cycle_menu = ttk.Combobox(
            self.target_window_cycle_frame,
            textvariable=self.target_window_cycle_var,
            values=["next", "prev"],
            state="readonly",
            width=12,
            font=("Microsoft YaHei UI", 9)
        )
        self.target_window_cycle_menu.pack(side="left", padx=(5, 0))

        # === command: 文本框 ===
        self.target_command_frame = tk.Frame(row2_container, bg=self.colors["bg_secondary"])

        command_left = tk.Frame(self.target_command_frame, bg=self.colors["bg_secondary"])
        command_left.pack(side="left", fill="x", expand=True)

        self.create_label(command_left, "系统命令:", 9, "text_dim").pack(side="left")
        self.target_command_entry = tk.Entry(
            command_left,
            font=("Microsoft YaHei UI", 9),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            insertbackground=self.colors["accent"],
            bd=0,
            highlightbackground=self.colors["border"],
            highlightthickness=1,
            highlightcolor=self.colors["accent"]
        )
        self.target_command_entry.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=4)

        # 添加帮助按钮
        help_btn = tk.Button(
            self.target_command_frame,
            text="?",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=self.colors["border"],
            fg=self.colors["text"],
            activebackground=self.colors["accent"],
            activeforeground="#ffffff",
            bd=0,
            width=2,
            cursor="hand2",
            command=self._show_command_examples
        )
        help_btn.pack(side="left", padx=(5, 0))

        # hover效果
        help_btn.bind("<Enter>", lambda e: help_btn.configure(bg=self.colors["accent"], fg="#ffffff"))
        help_btn.bind("<Leave>", lambda e: help_btn.configure(bg=self.colors["border"], fg=self.colors["text"]))

        # 添加简短提示(第二行)
        command_hint = tk.Frame(self.target_command_frame, bg=self.colors["bg_secondary"])
        command_hint.pack(fill="x", pady=(3, 0))
        hint_text = self.create_label(
            command_hint,
            "💡 例如: notepad.exe, calc.exe, start https://google.com  |  点击 ? 查看更多示例",
            7,
            "text_dim"
        )
        hint_text.pack(side="left", padx=(70, 0))

        # 默认显示 keyboard 控件
        self.target_keyboard_frame.pack(fill="x", pady=(8, 5))

        # 第三行：提示文本
        row3 = tk.Frame(edit_inner, bg=self.colors["bg_secondary"])
        row3.pack(fill="x", pady=5)

        self.create_label(row3, "提示:", 9, "text_dim").pack(side="left")
        self.hint_entry = tk.Entry(row3, font=("Microsoft YaHei UI", 10),
                                   bg=self.colors["bg"], fg=self.colors["text"],
                                   insertbackground=self.colors["accent"], bd=0,
                                   highlightbackground=self.colors["border"],
                                   highlightthickness=1,
                                   highlightcolor=self.colors["accent"])
        self.hint_entry.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=4)

        # 输入框focus效果
        self.hint_entry.bind("<FocusIn>", lambda e: self._on_entry_focus_in(self.hint_entry))
        self.hint_entry.bind("<FocusOut>", lambda e: self._on_entry_focus_out(self.hint_entry))

    def _create_action_buttons(self, parent):
        """创建操作按钮"""
        btn_frame = tk.Frame(parent, bg=self.colors["bg"])
        btn_frame.pack(fill="x")

        # 左侧按钮
        left_btns = tk.Frame(btn_frame, bg=self.colors["bg"])
        left_btns.pack(side="left")

        self.add_btn = self.create_btn(left_btns, "➕ 添加", self._add_mapping,
                                       bg=self.colors["accent"], fg="#fff")
        self.add_btn.pack(side="left", padx=(0, 8))

        self.create_btn(left_btns, "🗑 删除", self._delete_mapping,
                       bg=self.colors["danger"], fg="#fff").pack(side="left", padx=(0, 8))

        self.create_btn(left_btns, "↺ 重置", self._reset_defaults,
                       bg=self.colors["warning"], fg="#fff").pack(side="left", padx=(0, 8))

        self.cancel_btn = self.create_btn(left_btns, "✕ 取消编辑", self._cancel_edit,
                                         bg=self.colors["border"], fg=self.colors["text"])

        # 右侧保存按钮
        self.create_btn(btn_frame, "💾 保存配置", self._save,
                       bg=self.colors["success"], fg="#fff").pack(side="right")

    def _create_menu_button(self, parent, text):
        """创建下拉菜单按钮"""
        btn = tk.Button(parent, text=text + " ▼", font=("Microsoft YaHei UI", 10, "bold"),
                        bg=self.colors["accent"],
                        fg="#ffffff",
                        activebackground=self.colors["accent_hover"],
                        bd=0, padx=10, pady=5, cursor="hand2",
                        relief="flat",
                        command=self._show_mode_menu)

        # hover效果
        btn.bind("<Enter>", lambda e: btn.configure(bg=self.colors["accent_hover"]))
        btn.bind("<Leave>", lambda e: btn.configure(bg=self.colors["accent"]))
        return btn

    def _show_mode_menu(self):
        """显示模式下拉菜单"""
        try:
            x = self.mode_menu_btn.winfo_rootx()
            y = self.mode_menu_btn.winfo_rooty() + self.mode_menu_btn.winfo_height()
            self.mode_menu.post(x, y)
            # 短暂改变按钮样式表示展开状态
            self.mode_menu_btn.configure(bg=self.colors["accent_hover"])
            self.window.after(150, lambda: self.mode_menu_btn.configure(bg=self.colors["accent"]))
        except:
            pass

    def _select_mode(self, mode_name):
        """选择模式"""
        self.mode_var.set(mode_name)
        self.mode_menu_btn.configure(text=mode_name + " ▼")
        mode = self._get_selected_mode()
        self.enabled_var.set(mode.enabled)
        self._update_enabled_btn()
        self._cancel_edit()
        self._refresh_list()

    def _get_selected_mode(self):
        """获取当前选中的模式"""
        idx = [m.name for m in self.manager.modes].index(self.mode_var.get())
        return self.manager.modes[idx]

    def _toggle_enabled(self):
        """切换启用状态"""
        mode = self._get_selected_mode()
        mode.enabled = not mode.enabled
        self.enabled_var.set(mode.enabled)
        self._update_enabled_btn()

    def _update_enabled_btn(self):
        """更新启用按钮显示"""
        if self.enabled_var.get():
            self.enabled_btn.configure(text="✓ 已启用", bg=self.colors["success"])
        else:
            self.enabled_btn.configure(text="✗ 已禁用", bg=self.colors["danger"])

    def _toggle_block(self):
        """切换屏蔽选项"""
        self.block_var.set(not self.block_var.get())
        self._update_block_btn()

    def _update_block_btn(self):
        """更新屏蔽按钮显示（不改变值）"""
        if self.block_var.get():
            self.block_btn.configure(text="☑ 屏蔽源键", bg=self.colors["accent"])
        else:
            self.block_btn.configure(text="☐ 不屏蔽", bg=self.colors["border"])

    def _on_scroll(self, first, last):
        """滚动条变化时的回调，用于自动显示/隐藏滚动条"""
        # 将滚动位置传给scrollbar
        self.scrollbar.set(first, last)

        # 判断是否需要显示滚动条
        # 当first为0.0且last为1.0时，说明所有内容都可见，不需要滚动条
        first_float = float(first)
        last_float = float(last)

        if first_float <= 0.0 and last_float >= 1.0:
            # 内容完全可见，隐藏滚动条
            self.scroll_frame.pack_forget()
        else:
            # 内容需要滚动，显示滚动条
            if not self.scroll_frame.winfo_ismapped():
                self.scroll_frame.pack(side="right", fill="y", before=self.tree.master)

    def _refresh_list(self):
        """刷新映射列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        mode = self._get_selected_mode()

        # 创建交替的背景色
        bg_colors = [self.colors["bg_secondary"],
                    "#252538" if self.colors["bg_secondary"] == "#2a2a3e" else "#2f2f42"]

        for i, mapping in enumerate(mode.mappings.values()):
            block_text = "✓" if mapping.block else "✗"
            tags = ("odd" if i % 2 else "even",)
            item = self.tree.insert("", "end", values=(mapping.source_key, mapping.target_key,
                                                      block_text, mapping.hint or "-"),
                                   tags=tags)

        # 标签样式
        self.tree.tag_configure("odd", background=bg_colors[0])
        self.tree.tag_configure("even", background=bg_colors[1])

        # 刷新后更新滚动条显示状态
        self.tree.update_idletasks()
        self.tree.event_generate("<<TreeviewUpdate>>")

    def _on_double_click(self, event):
        """双击编辑"""
        item = self.tree.identify_row(event.y)
        if not item:
            return

        values = self.tree.item(item)["values"]
        source, target, block, hint = values

        # 从实际的 mapping 对象中获取 action_type
        mode = self._get_selected_mode()
        mapping = mode.mappings.get(str(source))
        action_type = mapping.action_type if mapping else "keyboard"

        # 进入编辑模式
        self.editing_source = str(source)
        self.edit_title.configure(text=f"编辑映射: {source}", fg=self.colors["warning"])
        self.add_btn.configure(text="✓ 更新")

        # 填充源键
        self.source_entry.delete(0, "end")
        self.source_entry.insert(0, source)

        # 填充提示
        self.hint_entry.delete(0, "end")
        self.hint_entry.insert(0, hint if hint != "-" else "")

        # 填充屏蔽选项
        self.block_var.set(block == "✓")
        self._update_block_btn()

        # 设置动作类型并切换显示相应的输入控件
        if action_type in self.action_type_code_map:
            self.action_type_menu.set(self.action_type_code_map[action_type])
            self._on_action_type_changed()  # 切换显示的控件

        # 根据动作类型填充目标输入控件
        if action_type == "keyboard":
            self.target_keyboard_entry.delete(0, "end")
            self.target_keyboard_entry.insert(0, target)
        elif action_type == "mouse_scroll":
            # 解析 "down:3" 格式
            parts = str(target).split(":")
            if len(parts) >= 2:
                direction = parts[0].strip()
                amount = parts[1].strip()
                self.target_scroll_direction_var.set(direction)
                self.target_scroll_amount_entry.delete(0, "end")
                self.target_scroll_amount_entry.insert(0, amount)
        elif action_type == "mouse_click":
            self.target_mouse_click_var.set(str(target))
        elif action_type == "window_cycle":
            self.target_window_cycle_var.set(str(target))
        elif action_type == "command":
            self.target_command_entry.delete(0, "end")
            self.target_command_entry.insert(0, target)

        # 显示取消按钮
        self.cancel_btn.pack(side="left", padx=(0, 8))

    def _cancel_edit(self):
        """取消编辑模式"""
        self.editing_source = None
        self.edit_title.configure(text="添加新映射", fg=self.colors["accent"])
        self.add_btn.configure(text="➕ 添加")
        self.cancel_btn.pack_forget()

        # 清空源键输入
        self.source_entry.delete(0, "end")

        # 清空提示输入
        self.hint_entry.delete(0, "end")

        # 重置屏蔽选项
        self.block_var.set(True)
        self.block_btn.configure(text="☑ 屏蔽源键", bg=self.colors["accent"])

        # 清空所有目标输入控件
        if self.target_keyboard_entry:
            self.target_keyboard_entry.delete(0, "end")

        if self.target_scroll_direction_var:
            self.target_scroll_direction_var.set("down")
        if self.target_scroll_amount_entry:
            self.target_scroll_amount_entry.delete(0, "end")
            self.target_scroll_amount_entry.insert(0, "1")

        if self.target_mouse_click_var:
            self.target_mouse_click_var.set("left")

        if self.target_window_cycle_var:
            self.target_window_cycle_var.set("next")

        if self.target_command_entry:
            self.target_command_entry.delete(0, "end")

        # 重置动作类型为默认值(keyboard)
        if self.action_type_menu:
            self.action_type_menu.current(0)  # 选择第一项（keyboard）
            self._on_action_type_changed()  # 切换显示keyboard控件

    def _add_mapping(self):
        """添加或更新映射"""
        source = self.source_entry.get().strip()
        hint = self.hint_entry.get().strip()

        if not source:
            messagebox.showwarning("提示", "源键不能为空")
            return

        # 获取action_type（从显示值转换为代码值）
        selected_display = self.action_type_menu.get()
        action_type = self.action_type_display_map.get(selected_display, "keyboard")

        # 根据动作类型获取目标字符串
        target = None
        if action_type == "keyboard":
            target = self.target_keyboard_entry.get().strip()
        elif action_type == "mouse_scroll":
            direction = self.target_scroll_direction_var.get()
            amount = self.target_scroll_amount_entry.get().strip()
            if not amount.isdigit():
                messagebox.showwarning("提示", "滚动量必须是数字")
                return
            target = f"{direction}:{amount}"
        elif action_type == "mouse_click":
            target = self.target_mouse_click_var.get()
        elif action_type == "window_cycle":
            target = self.target_window_cycle_var.get()
        elif action_type == "command":
            target = self.target_command_entry.get().strip()

        if not target:
            messagebox.showwarning("提示", "目标动作不能为空")
            return

        mode = self._get_selected_mode()

        # 如果是编辑模式，先删除旧映射
        if self.editing_source and self.editing_source != source:
            mode.remove_mapping(self.editing_source)

        # 创建新的 KeyMapping 对象（包含 action_type）
        from ..core.models import KeyMapping
        mapping = KeyMapping(source, target, self.block_var.get(), hint, action_type)
        mode.mappings[source] = mapping

        self._refresh_list()
        self._cancel_edit()

    def _delete_mapping(self):
        """删除选中映射"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的映射")
            return

        mode = self._get_selected_mode()
        for item in selected:
            source = self.tree.item(item)["values"][0]
            mode.remove_mapping(str(source))
        self._refresh_list()
        self._cancel_edit()

    def _reset_defaults(self):
        """恢复默认"""
        if messagebox.askyesno("确认", "确定要恢复默认设置吗？\n当前模式的所有自定义映射将丢失。"):
            mode = self._get_selected_mode()
            mode.load_defaults()
            self._refresh_list()
            self._cancel_edit()

    def _save(self):
        """保存配置"""
        # 保存按键映射配置
        self.manager.save_config()

        # 保存高级设置
        try:
            from wheel_tool.config.settings import GlobalConfig
            from wheel_tool.system.startup_manager import StartupManager

            # 保存提示显示设置
            GlobalConfig.set('hint_overlay.enabled', self.hint_enabled_var.get())

            try:
                duration = int(self.hint_duration_var.get())
                GlobalConfig.set('hint_overlay.display_duration', duration)
            except ValueError:
                messagebox.showwarning("警告", "显示时长必须是整数")

            try:
                alpha = float(self.hint_alpha_var.get())
                if 0 <= alpha <= 1:
                    GlobalConfig.set('hint_overlay.alpha', alpha)
                else:
                    messagebox.showwarning("警告", "透明度必须在0-1之间")
            except ValueError:
                messagebox.showwarning("警告", "透明度必须是数字")

            try:
                fontsize = int(self.hint_fontsize_var.get())
                GlobalConfig.set('hint_overlay.font_size', fontsize)
            except ValueError:
                messagebox.showwarning("警告", "字体大小必须是整数")

            try:
                width = int(self.hint_width_var.get())
                GlobalConfig.set('hint_overlay.width', width)
            except ValueError:
                messagebox.showwarning("警告", "窗口宽度必须是整数")

            try:
                height = int(self.hint_height_var.get())
                GlobalConfig.set('hint_overlay.height', height)
            except ValueError:
                messagebox.showwarning("警告", "窗口高度必须是整数")

            try:
                margin = int(self.hint_margin_var.get())
                GlobalConfig.set('hint_overlay.bottom_margin', margin)
            except ValueError:
                messagebox.showwarning("警告", "底部边距必须是整数")

            # 保存热键设置
            GlobalConfig.set('hotkeys.next_mode', self.hotkey_next_var.get().strip())
            GlobalConfig.set('hotkeys.prev_mode', self.hotkey_prev_var.get().strip())
            GlobalConfig.set('hotkeys.open_settings', self.hotkey_settings_var.get().strip())
            GlobalConfig.set('hotkeys.hide_disk', self.hotkey_hide_var.get().strip())

            # 保存开机启动设置
            startup_enabled = self.startup_enabled_var.get()
            GlobalConfig.set('startup.enabled', startup_enabled)

            # 应用开机启动设置到系统
            if startup_enabled:
                if not StartupManager.enable():
                    messagebox.showerror("错误", "启用开机启动失败，请检查系统权限")
            else:
                if not StartupManager.disable():
                    messagebox.showerror("错误", "禁用开机启动失败，请检查系统权限")

            # 保存到文件
            GlobalConfig.save()

            messagebox.showinfo("保存成功", "配置已保存到文件！\n\n修改热键需要重启程序才能生效。")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存高级设置失败: {e}")

    def _show_command_examples(self):
        """显示系统命令示例"""
        examples_text = """常用系统命令示例：

📝 文本编辑器
• notepad.exe              (打开记事本)
• notepad C:\\path\\to\\file.txt (打开指定文件)

🌐 浏览器
• start https://www.google.com  (打开网页)
• start chrome.exe              (启动Chrome)
• start firefox.exe             (启动Firefox)

📂 文件管理
• explorer C:\\Users            (打开指定文件夹)
• explorer /select,C:\\file.txt (选中文件)

🎵 媒体应用
• start wmplayer.exe           (Windows媒体播放器)
• start spotify.exe            (Spotify)

⚙ 系统工具
• calc.exe                     (计算器)
• mspaint.exe                  (画图)
• snippingtool.exe             (截图工具)
• taskmgr.exe                  (任务管理器)

🔧 系统操作
• shutdown /s /t 0             (立即关机)
• shutdown /r /t 0             (立即重启)
• shutdown /l                  (注销)
• rundll32 user32.dll,LockWorkStation (锁定)

💡 提示：
- 使用完整路径可避免找不到程序
- 路径中有空格需要加引号: "C:\\Program Files\\app.exe"
- start 命令可以打开文件、文件夹和网址
"""
        messagebox.showinfo("系统命令示例", examples_text)

    def _start_record(self, entry):
        """开始录制按键（支持组合键）"""
        self.recording_entry = entry
        entry.delete(0, "end")
        entry.insert(0, "按任意键...")
        entry.configure(bg=self.colors["accent"])
        entry.focus_set()

        def on_key(event):
            # 调试输出
            print(f"[录制] keysym={event.keysym}, state={hex(event.state)}, char={repr(event.char)}")

            # 获取原始键名
            raw_key = event.keysym.lower()

            # Tkinter键名到系统键名的映射表
            key_map = {
                'control_l': 'ctrl', 'control_r': 'ctrl',
                'shift_l': 'shift', 'shift_r': 'shift',
                'alt_l': 'alt', 'alt_r': 'alt',
                'win_l': 'win', 'win_r': 'win',
                'prior': 'page_up', 'next': 'page_down',
                'return': 'enter',
            }

            # 标准化键名
            main_key = key_map.get(raw_key, raw_key)

            # 如果按下的是纯修饰键，跳过（等待主键）
            if main_key in ['ctrl', 'shift', 'alt', 'win']:
                print(f"[录制] 跳过修饰键: {main_key}")
                return "break"  # 阻止事件传播

            # 检测修饰键状态
            modifiers = []
            # Shift=0x1, Ctrl=0x4, Alt=0x20000 (或 0x80)
            if event.state & 0x4:  # Ctrl
                modifiers.append('ctrl')
            if event.state & 0x20000:  # Alt (Windows)
                if 'alt' not in modifiers:
                    modifiers.append('alt')
            if event.state & 0x80:  # Alt (某些系统)
                if 'alt' not in modifiers:
                    modifiers.append('alt')
            if event.state & 0x1:  # Shift
                modifiers.append('shift')

            # 组合完整按键字符串
            if modifiers:
                result = '+'.join(modifiers + [main_key])
            else:
                result = main_key

            print(f"[录制] 结果: {result}")

            # 更新输入框并结束录制
            entry.delete(0, "end")
            entry.insert(0, result)
            entry.configure(bg=self.colors["bg"])
            entry.unbind("<KeyPress>")
            self.recording_entry = None

            return "break"  # 阻止事件传播到Entry的默认处理

        entry.bind("<KeyPress>", on_key)

    def _preview_hint(self):
        """测试预览提示显示效果"""
        try:
            # 读取当前配置
            config = {
                'enabled': self.hint_enabled_var.get(),
                'display_duration': int(self.hint_duration_var.get()),
                'alpha': float(self.hint_alpha_var.get()),
                'font_size': int(self.hint_fontsize_var.get()),
                'width': int(self.hint_width_var.get()),
                'height': int(self.hint_height_var.get()),
                'bottom_margin': int(self.hint_margin_var.get()),
            }

            # 验证配置
            if not 0 <= config['alpha'] <= 1:
                messagebox.showwarning("警告", "透明度必须在0-1之间")
                return

            # 创建临时的 HintOverlay 用于预览
            from wheel_tool.ui.hint_overlay import HintOverlay

            # 获取主窗口作为父窗口
            parent = self.window

            # 创建临时预览窗口
            preview_hint = HintOverlay(parent=parent)
            preview_hint.hint_config = config
            preview_hint.width = config['width']
            preview_hint.height = config['height']
            preview_hint.create_window()

            # 显示测试文本
            preview_hint.show("这是测试提示 🎉")

            messagebox.showinfo("预览", "正在显示测试提示！\n\n提示将在 {:.1f} 秒后自动消失。".format(config['display_duration'] / 1000))

        except ValueError as e:
            messagebox.showerror("错误", f"配置值格式错误:\n{e}")

    def _create_advanced_settings(self, parent):
        """创建高级设置区域"""
        advanced_inner = tk.Frame(parent, bg=self.colors["bg_secondary"])
        advanced_inner.pack(fill="x", padx=15, pady=12)

        # 标题
        header = tk.Frame(advanced_inner, bg=self.colors["bg_secondary"])
        header.pack(fill="x", pady=(0, 10))

        self.create_label(header, "⚙ 高级设置", 10, "text", bold=True).pack(side="left")

        # 加载配置
        from wheel_tool.config.settings import GlobalConfig
        config = GlobalConfig.load()

        # === 提示显示设置 ===
        hint_section = tk.Frame(advanced_inner, bg=self.colors["bg_secondary"])
        hint_section.pack(fill="x", pady=(0, 15))

        self.create_label(hint_section, "💬 提示显示设置", 9, "accent", bold=True).pack(anchor="w", pady=(0, 8))

        # 第一行：启用开关和显示时长
        hint_row1 = tk.Frame(hint_section, bg=self.colors["bg_secondary"])
        hint_row1.pack(fill="x", pady=3)

        # 启用开关
        self.hint_enabled_var = tk.BooleanVar(value=config.get('hint_overlay', {}).get('enabled', True))
        hint_enabled_btn = tk.Checkbutton(
            hint_row1, text="启用提示显示",
            variable=self.hint_enabled_var,
            bg=self.colors["bg_secondary"], fg=self.colors["text"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg_secondary"],
            activeforeground=self.colors["text"],
            font=("Microsoft YaHei UI", 9),
            cursor="hand2"
        )
        hint_enabled_btn.pack(side="left", padx=(0, 20))

        # 显示时长
        self.create_label(hint_row1, "显示时长(ms):", 9, "text_dim").pack(side="left", padx=(0, 5))
        self.hint_duration_var = tk.StringVar(value=str(config.get('hint_overlay', {}).get('display_duration', 1200)))
        hint_duration_entry = self.create_entry(hint_row1, width=8, textvariable=self.hint_duration_var)
        hint_duration_entry.pack(side="left", ipady=2)

        # 第二行：透明度和字体大小
        hint_row2 = tk.Frame(hint_section, bg=self.colors["bg_secondary"])
        hint_row2.pack(fill="x", pady=3)

        # 透明度
        self.create_label(hint_row2, "透明度(0-1):", 9, "text_dim").pack(side="left", padx=(0, 5))
        self.hint_alpha_var = tk.StringVar(value=str(config.get('hint_overlay', {}).get('alpha', 0.85)))
        hint_alpha_entry = self.create_entry(hint_row2, width=8, textvariable=self.hint_alpha_var)
        hint_alpha_entry.pack(side="left", padx=(0, 20), ipady=2)

        # 字体大小
        self.create_label(hint_row2, "字体大小:", 9, "text_dim").pack(side="left", padx=(0, 5))
        self.hint_fontsize_var = tk.StringVar(value=str(config.get('hint_overlay', {}).get('font_size', 24)))
        hint_fontsize_entry = self.create_entry(hint_row2, width=8, textvariable=self.hint_fontsize_var)
        hint_fontsize_entry.pack(side="left", ipady=2)

        # 第三行：宽度和高度
        hint_row3 = tk.Frame(hint_section, bg=self.colors["bg_secondary"])
        hint_row3.pack(fill="x", pady=3)

        self.create_label(hint_row3, "窗口宽度(px):", 9, "text_dim").pack(side="left", padx=(0, 5))
        self.hint_width_var = tk.StringVar(value=str(config.get('hint_overlay', {}).get('width', 400)))
        hint_width_entry = self.create_entry(hint_row3, width=8, textvariable=self.hint_width_var)
        hint_width_entry.pack(side="left", padx=(0, 20), ipady=2)

        self.create_label(hint_row3, "窗口高度(px):", 9, "text_dim").pack(side="left", padx=(0, 5))
        self.hint_height_var = tk.StringVar(value=str(config.get('hint_overlay', {}).get('height', 80)))
        hint_height_entry = self.create_entry(hint_row3, width=8, textvariable=self.hint_height_var)
        hint_height_entry.pack(side="left", ipady=2)

        # 第四行：底部边距
        hint_row4 = tk.Frame(hint_section, bg=self.colors["bg_secondary"])
        hint_row4.pack(fill="x", pady=3)

        self.create_label(hint_row4, "底部边距(px):", 9, "text_dim").pack(side="left", padx=(0, 5))
        self.hint_margin_var = tk.StringVar(value=str(config.get('hint_overlay', {}).get('bottom_margin', 100)))
        hint_margin_entry = self.create_entry(hint_row4, width=8, textvariable=self.hint_margin_var)
        hint_margin_entry.pack(side="left", ipady=2)

        # === 热键设置 ===
        hotkey_section = tk.Frame(advanced_inner, bg=self.colors["bg_secondary"])
        hotkey_section.pack(fill="x", pady=(0, 0))

        self.create_label(hotkey_section, "⌨ 全局热键设置", 9, "accent", bold=True).pack(anchor="w", pady=(0, 8))

        # 第一行：下一模式和上一模式
        hotkey_row1 = tk.Frame(hotkey_section, bg=self.colors["bg_secondary"])
        hotkey_row1.pack(fill="x", pady=3)

        self.create_label(hotkey_row1, "下一模式:", 9, "text_dim").pack(side="left", padx=(0, 5))
        self.hotkey_next_var = tk.StringVar(value=config.get('hotkeys', {}).get('next_mode', 'ctrl+alt+shift+-'))
        hotkey_next_entry = self.create_entry(hotkey_row1, width=20, textvariable=self.hotkey_next_var)
        hotkey_next_entry.pack(side="left", padx=(0, 3), ipady=2)

        self.create_btn(hotkey_row1, "录", lambda: self._start_record(hotkey_next_entry),
                       bg=self.colors["border"], width=3).pack(side="left", padx=(0, 15))

        self.create_label(hotkey_row1, "上一模式:", 9, "text_dim").pack(side="left", padx=(0, 5))
        self.hotkey_prev_var = tk.StringVar(value=config.get('hotkeys', {}).get('prev_mode', 'ctrl+alt+shift+='))
        hotkey_prev_entry = self.create_entry(hotkey_row1, width=20, textvariable=self.hotkey_prev_var)
        hotkey_prev_entry.pack(side="left", padx=(0, 3), ipady=2)

        self.create_btn(hotkey_row1, "录", lambda: self._start_record(hotkey_prev_entry),
                       bg=self.colors["border"], width=3).pack(side="left")

        # 第二行：打开设置和隐藏圆盘
        hotkey_row2 = tk.Frame(hotkey_section, bg=self.colors["bg_secondary"])
        hotkey_row2.pack(fill="x", pady=3)

        self.create_label(hotkey_row2, "打开设置:", 9, "text_dim").pack(side="left", padx=(0, 5))
        self.hotkey_settings_var = tk.StringVar(value=config.get('hotkeys', {}).get('open_settings', 'ctrl+alt+shift+s'))
        hotkey_settings_entry = self.create_entry(hotkey_row2, width=20, textvariable=self.hotkey_settings_var)
        hotkey_settings_entry.pack(side="left", padx=(0, 3), ipady=2)

        self.create_btn(hotkey_row2, "录", lambda: self._start_record(hotkey_settings_entry),
                       bg=self.colors["border"], width=3).pack(side="left", padx=(0, 15))

        self.create_label(hotkey_row2, "隐藏圆盘:", 9, "text_dim").pack(side="left", padx=(0, 5))
        self.hotkey_hide_var = tk.StringVar(value=config.get('hotkeys', {}).get('hide_disk', 'esc'))
        hotkey_hide_entry = self.create_entry(hotkey_row2, width=20, textvariable=self.hotkey_hide_var)
        hotkey_hide_entry.pack(side="left", padx=(0, 3), ipady=2)

        self.create_btn(hotkey_row2, "录", lambda: self._start_record(hotkey_hide_entry),
                       bg=self.colors["border"], width=3).pack(side="left")

        # 提示信息
        tip_frame = tk.Frame(advanced_inner, bg=self.colors["bg_secondary"])
        tip_frame.pack(fill="x", pady=(10, 0))

        self.create_label(tip_frame, "💡 提示: 修改热键后需要重启程序才能生效",
                         8, "warning").pack(anchor="w")

        # === 开机启动设置 ===
        startup_section = tk.Frame(advanced_inner, bg=self.colors["bg_secondary"])
        startup_section.pack(fill="x", pady=(15, 0))

        self.create_label(startup_section, "🚀 开机启动设置", 9, "accent", bold=True).pack(anchor="w", pady=(0, 8))

        # 开机启动开关
        startup_row = tk.Frame(startup_section, bg=self.colors["bg_secondary"])
        startup_row.pack(fill="x", pady=3)

        # 从StartupManager获取实际状态
        from wheel_tool.system.startup_manager import StartupManager
        actual_startup_enabled = StartupManager.is_enabled()

        # 如果配置文件中的状态与实际状态不一致，以实际状态为准
        config_startup_enabled = config.get('startup', {}).get('enabled', False)
        if actual_startup_enabled != config_startup_enabled:
            # 同步配置文件
            GlobalConfig.set('startup.enabled', actual_startup_enabled)
            GlobalConfig.save()

        self.startup_enabled_var = tk.BooleanVar(value=actual_startup_enabled)
        startup_enabled_btn = tk.Checkbutton(
            startup_row, text="开机自动启动",
            variable=self.startup_enabled_var,
            bg=self.colors["bg_secondary"], fg=self.colors["text"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg_secondary"],
            activeforeground=self.colors["text"],
            font=("Microsoft YaHei UI", 9),
            cursor="hand2"
        )
        startup_enabled_btn.pack(side="left", padx=(0, 10))

        # 状态提示
        startup_status_label = self.create_label(
            startup_row,
            "启用后程序将在Windows登录时自动运行",
            8,
            "text_dim"
        )
        startup_status_label.pack(side="left")