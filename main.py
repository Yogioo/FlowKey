#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圆盘模式切换工具 - 主程序入口
Wheel Disk Mode Switch Tool - Main Entry Point

这是一个统一的程序入口脚本，整合了所有重构后的模块化组件。
This is a unified entry point script that integrates all refactored modular components.

运行方式:
    python main.py

功能特性:
    - 模块化架构设计
    - 支持快捷键映射配置
    - 系统托盘图标支持
    - 动画效果支持
    - 完整的错误处理和日志记录
"""

import sys
import logging
import warnings
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# 导入重构后的模块化组件
from key_mapper import ModeManager, MappingPanel
from wheel_tool import WheelDisk, WheelToolApp
from wheel_tool.input.controller import ModeController
from wheel_tool.input.hotkey_listener import HotkeyListener
from wheel_tool.config.settings import GlobalConfig


def setup_logging():
    """设置日志记录"""
    # 过滤不必要的警告
    warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")
    warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*pkg_resources.*")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('wheel_tool.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def initialize_components():
    """初始化所有组件"""
    logger = logging.getLogger(__name__)

    try:
        # 1. 初始化模式管理器
        logger.info("初始化模式管理器...")
        mode_manager = ModeManager()

        # 2. 初始化圆盘界面
        logger.info("初始化圆盘界面...")
        disk = WheelDisk()

        # 3. 初始化模式控制器
        logger.info("初始化模式控制器...")
        controller = ModeController(disk)

        # 4. 初始化设置面板（需要在热键监听器之前创建）
        logger.info("初始化设置面板...")
        settings_panel = MappingPanel(mode_manager)

        # 5. 初始化热键监听器
        logger.info("初始化热键监听器...")
        listener = HotkeyListener(disk, controller, mode_manager, settings_panel)

        # 6. 初始化全局配置
        logger.info("加载全局配置...")
        config = GlobalConfig()

        logger.info("所有组件初始化完成")

        return {
            'mode_manager': mode_manager,
            'disk': disk,
            'listener': listener,
            'settings_panel': settings_panel,
            'config': config
        }

    except Exception as e:
        logger.error(f"组件初始化失败: {e}")
        raise


def sync_startup_setting():
    """同步开机启动设置"""
    logger = logging.getLogger(__name__)

    try:
        from wheel_tool.system.startup_manager import StartupManager

        # 加载配置
        config = GlobalConfig.load()
        config_enabled = config.get('startup', {}).get('enabled', False)

        # 获取实际系统状态
        actual_enabled = StartupManager.is_enabled()

        # 如果配置与实际状态不一致，以配置为准，重新应用
        if config_enabled != actual_enabled:
            logger.info(f"同步开机启动设置: 配置={config_enabled}, 实际={actual_enabled}")

            if config_enabled:
                if StartupManager.enable():
                    logger.info("✅ 已启用开机启动")
                else:
                    logger.warning("⚠ 启用开机启动失败")
            else:
                if StartupManager.disable():
                    logger.info("✅ 已禁用开机启动")
                else:
                    logger.warning("⚠ 禁用开机启动失败")
        else:
            logger.info(f"开机启动设置已同步: {config_enabled}")

    except Exception as e:
        logger.error(f"同步开机启动设置失败: {e}")



def create_application():
    """创建应用程序实例"""
    logger = logging.getLogger(__name__)
    
    try:
        # 初始化所有组件
        components = initialize_components()
        
        # 创建主应用程序
        logger.info("创建主应用程序实例...")
        app = WheelToolApp(
            mode_manager=components['mode_manager'],
            disk=components['disk'],
            listener=components['listener'],
            settings_panel=components['settings_panel']
        )
        
        logger.info("✅ 应用程序创建完成")
        return app, components['config']
        
    except Exception as e:
        logger.error(f"应用程序创建失败: {e}")
        raise


def check_dependencies():
    """检查必要的依赖"""
    logger = logging.getLogger(__name__)
    
    required_modules = [
        'tkinter',
        'keyboard',
        'PIL'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"缺少必要的依赖模块: {', '.join(missing_modules)}")
        logger.error("请安装缺少的模块: pip install " + " ".join(missing_modules))
        return False
    
    logger.info("所有依赖模块检查通过")
    return True


def main():
    """主函数"""
    # 设置日志
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("启动圆盘模式切换工具 v2.0")
    logger.info("模块化架构版本")
    logger.info("=" * 60)

    try:
        # 检查依赖
        if not check_dependencies():
            sys.exit(1)

        # 同步开机启动设置
        sync_startup_setting()

        # 创建应用程序
        app, config = create_application()

        # 启动应用程序
        logger.info("启动应用程序...")
        app.start()

    except KeyboardInterrupt:
        logger.info("用户主动退出程序")
    except Exception as e:
        logger.error(f"程序运行时发生错误: {e}")
        logger.exception("详细错误信息:")
        sys.exit(1)
    finally:
        logger.info("程序已退出")


if __name__ == "__main__":
    main()