# -*- coding: utf-8 -*-
"""
测试配置UI中的窗口切换选项
"""

import sys
sys.path.insert(0, r"E:\Desktop\f")

from key_mapper.core.manager import ModeManager
from key_mapper.ui.mapping_panel import MappingPanel

# 创建模式管理器
manager = ModeManager()

# 创建配置面板
panel = MappingPanel(manager)

# 显示配置面板
panel.show()

print("配置面板已打开！")
print("请检查：")
print("1. 切换到'窗口管理'模式")
print("2. 查看默认映射中是否有 f23 和 f24")
print("3. 尝试添加新映射时，动作类型下拉菜单中是否有'🪟 窗口切换'选项")
print("4. 选择'窗口切换'后，提示文本是否显示正确")

# 保持窗口运行
try:
    panel.window.mainloop()
except KeyboardInterrupt:
    pass
