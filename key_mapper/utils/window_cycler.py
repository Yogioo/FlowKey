# -*- coding: utf-8 -*-
"""
窗口循环切换器
使用 Windows API 实现真正的窗口遍历功能
"""

import ctypes
import ctypes.wintypes as wintypes
from typing import List, Dict, Optional
from comtypes import GUID, COMMETHOD
from ctypes import POINTER, c_int, HRESULT
import comtypes.client


class WindowInfo:
    """窗口信息"""
    def __init__(self, hwnd: int, title: str):
        self.hwnd = hwnd
        self.title = title

    def __repr__(self):
        return f"Window(hwnd={self.hwnd}, title='{self.title}')"


class WindowCycler:
    """窗口循环切换器 - 实现真正的窗口遍历而非 Alt+Tab 来回切换"""

    def __init__(self):
        self.windows: List[WindowInfo] = []
        self.current_index = 0
        self._init_windows_api()
        self._init_virtual_desktop_manager()

    def _init_windows_api(self):
        """初始化 Windows API 函数"""
        # 定义 Windows API 函数类型
        self.EnumWindows = ctypes.windll.user32.EnumWindows
        self.IsWindowVisible = ctypes.windll.user32.IsWindowVisible
        self.GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW
        self.GetWindowTextW = ctypes.windll.user32.GetWindowTextW
        self.GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
        self.SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
        self.IsIconic = ctypes.windll.user32.IsIconic  # 检查窗口是否最小化
        self.ShowWindow = ctypes.windll.user32.ShowWindow
        self.BringWindowToTop = ctypes.windll.user32.BringWindowToTop
        self.SwitchToThisWindow = ctypes.windll.user32.SwitchToThisWindow
        self.GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
        self.AttachThreadInput = ctypes.windll.user32.AttachThreadInput
        self.GetCurrentThreadId = ctypes.windll.kernel32.GetCurrentThreadId

        # Windows 常量
        self.SW_RESTORE = 9  # 恢复窗口
        self.SW_SHOW = 5  # 显示窗口

    def _init_virtual_desktop_manager(self):
        """初始化虚拟桌面管理器"""
        try:
            # IVirtualDesktopManager 的 CLSID 和 IID
            CLSID_VirtualDesktopManager = GUID("{AA509086-5CA9-4C25-8F95-589D3C07B48A}")
            IID_IVirtualDesktopManager = GUID("{A5CD92FF-29BE-454C-8D04-D82879FB3F1B}")

            # 创建 VirtualDesktopManager 实例
            ole32 = ctypes.windll.ole32
            ole32.CoInitialize(None)

            # 使用 comtypes 创建 COM 对象
            import comtypes
            from comtypes import CoCreateInstance

            # 定义 IVirtualDesktopManager 接口
            class IVirtualDesktopManager(comtypes.IUnknown):
                _iid_ = IID_IVirtualDesktopManager
                _methods_ = [
                    COMMETHOD([], HRESULT, 'IsWindowOnCurrentVirtualDesktop',
                              (['in'], wintypes.HWND, 'topLevelWindow'),
                              (['out'], POINTER(c_int), 'onCurrentDesktop')),
                    COMMETHOD([], HRESULT, 'GetWindowDesktopId',
                              (['in'], wintypes.HWND, 'topLevelWindow'),
                              (['out'], POINTER(GUID), 'desktopId')),
                    COMMETHOD([], HRESULT, 'MoveWindowToDesktop',
                              (['in'], wintypes.HWND, 'topLevelWindow'),
                              (['in'], POINTER(GUID), 'desktopId')),
                ]

            self.vd_manager = CoCreateInstance(
                CLSID_VirtualDesktopManager,
                interface=IVirtualDesktopManager
            )
            print("[窗口切换器] 虚拟桌面管理器已初始化")
        except Exception as e:
            print(f"[窗口切换器] 无法初始化虚拟桌面管理器: {e}")
            self.vd_manager = None

    def _is_window_on_current_desktop(self, hwnd: int) -> bool:
        """检查窗口是否在当前虚拟桌面上"""
        if not self.vd_manager:
            return True  # 如果无法初始化，就不过滤

        try:
            on_current = c_int()
            hr = self.vd_manager.IsWindowOnCurrentVirtualDesktop(hwnd, ctypes.byref(on_current))
            if hr == 0:  # S_OK
                return bool(on_current.value)
            else:
                return True  # 如果检查失败，保留窗口
        except Exception as e:
            # print(f"[窗口切换器] 检查虚拟桌面失败 (hwnd={hwnd}): {e}")
            return True  # 出错时保留窗口

    def refresh_windows(self):
        """刷新可见窗口列表"""
        self.windows = []

        def enum_handler(hwnd, ctx):
            # 只处理可见且有标题的窗口
            if self.IsWindowVisible(hwnd):
                length = self.GetWindowTextLengthW(hwnd)
                if length > 0:
                    # 获取窗口标题
                    title = ctypes.create_unicode_buffer(length + 1)
                    self.GetWindowTextW(hwnd, title, length + 1)

                    # 过滤掉某些系统窗口
                    title_str = title.value
                    if self._should_include_window(hwnd, title_str):
                        # 检查窗口是否在当前虚拟桌面
                        if self._is_window_on_current_desktop(hwnd):
                            self.windows.append(WindowInfo(hwnd, title_str))
            return True

        # 定义回调函数类型
        EnumWindowsProc = ctypes.WINFUNCTYPE(
            wintypes.BOOL,
            wintypes.HWND,
            wintypes.LPARAM
        )

        # 枚举所有顶层窗口
        self.EnumWindows(EnumWindowsProc(enum_handler), 0)

        # 更新当前窗口索引
        fg_hwnd = self.GetForegroundWindow()
        for i, win in enumerate(self.windows):
            if win.hwnd == fg_hwnd:
                self.current_index = i
                break

        print(f"[窗口切换器] 发现 {len(self.windows)} 个窗口")

    def _should_include_window(self, hwnd: int, title: str) -> bool:
        """判断是否应该包含此窗口"""
        # 过滤掉空标题或特定系统窗口
        exclude_titles = [
            "Program Manager",  # Windows 桌面
            "Windows Input Experience",  # 输入法面板
            "Microsoft Text Input Application",  # 微软输入法
        ]

        # 过滤掉包含特定关键词的窗口标题
        exclude_keywords = [
            "Overlay",  # 各种覆盖层窗口
            "ToastWindow",  # 通知窗口
        ]

        # 排除特定标题
        if title in exclude_titles:
            return False

        # 排除包含关键词的标题
        for keyword in exclude_keywords:
            if keyword in title:
                return False

        # 可以添加更多过滤规则，比如：
        # - 过滤掉不可见的窗口
        # - 过滤掉没有图标的窗口
        # - 过滤掉特定类名的窗口

        return True

    def switch_next(self) -> Optional[WindowInfo]:
        """
        切换到下一个窗口
        使用模拟 Alt+Tab 的方式，更可靠

        Returns:
            切换到的窗口信息，如果失败返回 None
        """
        # 使用 keyboard 模拟 Alt+Tab
        try:
            import keyboard
            # 按下 Alt+Tab 切换到下一个窗口
            keyboard.press('alt')
            keyboard.press_and_release('tab')
            keyboard.release('alt')

            # 短暂等待切换完成
            import time
            time.sleep(0.1)

            # 获取切换后的窗口信息
            result = self.get_current_window()
            if result:
                print(f"[窗口切换器] 切换到: {result.title}")
            return result
        except Exception as e:
            print(f"[窗口切换器] 切换失败: {e}")
            return None

    def switch_prev(self) -> Optional[WindowInfo]:
        """
        切换到上一个窗口
        使用模拟 Alt+Shift+Tab 的方式，更可靠

        Returns:
            切换到的窗口信息，如果失败返回 None
        """
        # 使用 keyboard 模拟 Alt+Shift+Tab
        try:
            import keyboard
            # 按下 Alt+Shift+Tab 切换到上一个窗口
            keyboard.press('alt')
            keyboard.press('shift')
            keyboard.press_and_release('tab')
            keyboard.release('shift')
            keyboard.release('alt')

            # 短暂等待切换完成
            import time
            time.sleep(0.1)

            # 获取切换后的窗口信息
            result = self.get_current_window()
            if result:
                print(f"[窗口切换器] 切换到: {result.title}")
            return result
        except Exception as e:
            print(f"[窗口切换器] 切换失败: {e}")
            return None

    def _activate_current(self) -> Optional[WindowInfo]:
        """
        激活当前索引的窗口

        Returns:
            激活的窗口信息，如果失败返回 None
        """
        if 0 <= self.current_index < len(self.windows):
            win = self.windows[self.current_index]

            try:
                # 如果窗口最小化，先恢复
                if self.IsIconic(win.hwnd):
                    self.ShowWindow(win.hwnd, self.SW_RESTORE)
                else:
                    self.ShowWindow(win.hwnd, self.SW_SHOW)

                # 使用多种方法尝试激活窗口，提高成功率
                success = False

                # 方法1: 使用 SwitchToThisWindow (最强制的方法)
                try:
                    self.SwitchToThisWindow(win.hwnd, True)
                    success = True
                except:
                    pass

                # 方法2: 线程输入附加技巧 + SetForegroundWindow
                if not success:
                    try:
                        # 获取前台窗口的线程ID
                        fg_hwnd = self.GetForegroundWindow()
                        fg_thread = self.GetWindowThreadProcessId(fg_hwnd, None)
                        # 获取目标窗口的线程ID
                        target_thread = self.GetWindowThreadProcessId(win.hwnd, None)
                        # 获取当前线程ID
                        current_thread = self.GetCurrentThreadId()

                        # 附加线程输入
                        if fg_thread != target_thread:
                            self.AttachThreadInput(current_thread, fg_thread, True)
                            self.AttachThreadInput(current_thread, target_thread, True)

                        # 尝试激活
                        self.BringWindowToTop(win.hwnd)
                        result = self.SetForegroundWindow(win.hwnd)

                        # 分离线程输入
                        if fg_thread != target_thread:
                            self.AttachThreadInput(current_thread, fg_thread, False)
                            self.AttachThreadInput(current_thread, target_thread, False)

                        if result:
                            success = True
                    except Exception as e:
                        print(f"[窗口切换器] 线程附加方法失败: {e}")

                # 方法3: 简单的 SetForegroundWindow (兜底)
                if not success:
                    self.BringWindowToTop(win.hwnd)
                    result = self.SetForegroundWindow(win.hwnd)
                    if result:
                        success = True

                if success:
                    print(f"[窗口切换器] 切换到: {win.title}")
                    return win
                else:
                    print(f"[窗口切换器] 切换失败: {win.title}")
                    return None

            except Exception as e:
                print(f"[窗口切换器] 激活窗口异常: {e}")
                return None

        return None

    def get_current_window(self) -> Optional[WindowInfo]:
        """获取当前活动窗口信息"""
        fg_hwnd = self.GetForegroundWindow()
        if fg_hwnd:
            length = self.GetWindowTextLengthW(fg_hwnd)
            if length > 0:
                title = ctypes.create_unicode_buffer(length + 1)
                self.GetWindowTextW(fg_hwnd, title, length + 1)
                return WindowInfo(fg_hwnd, title.value)
        return None

    def get_window_list(self) -> List[WindowInfo]:
        """获取所有窗口列表"""
        self.refresh_windows()
        return self.windows.copy()
