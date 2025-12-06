# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Wheel Disk Mode Switch Tool** (圆盘模式切换工具) - a Python application that provides a visual wheel disk UI for switching between different keyboard mapping modes. The tool features a circular overlay UI with mode-based hotkey remapping, system tray integration, and customizable key mappings.

**Key Functionality:**
- Visual circular disk overlay showing 4 modes: 浏览模式 (Browse), 影音模式 (Media), 视频模式 (Video), 窗口管理 (Window Management)
- Global hotkey interception and remapping based on active mode
- System tray icon with pause/resume functionality
- Configuration UI for managing key mappings per mode
- Auto-hide behavior with configurable delays

## Development Commands

### Running the Application
```bash
python main.py
```

### Running Tests
```bash
python test_disk_fixes.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

**Note:** The application requires administrator/elevated privileges on Windows for global keyboard hooking to work properly.

## Architecture Overview

### Two-Module System

The codebase is split into two primary modules that work together:

#### 1. `key_mapper/` - Key Mapping System
Manages keyboard mappings and mode definitions. This is the "data layer" that defines what keys should be mapped to what in each mode.

**Structure:**
- `core/manager.py` - `ModeManager`: Central manager that holds all modes, tracks current mode index, and handles mode switching
- `core/models.py` - `BaseMode`, `KeyMapping`: Abstract base class for modes and mapping data structures
- `core/modes.py` - Concrete mode implementations (BrowseMode, MediaMode, VideoMode, WindowMode)
- `config/storage.py` - `ConfigManager`: JSON persistence for key mappings (saves to `key_mappings.json`)
- `ui/mapping_panel.py` - `MappingPanel`: Tkinter settings UI for editing mappings per mode

#### 2. `wheel_tool/` - Visual Disk & Application Runtime
Handles the visual wheel disk UI, hotkey listening, and application lifecycle.

**Structure:**
- `ui/disk.py` - `WheelDisk`: The circular overlay UI rendered with PIL for antialiasing
- `ui/renderer.py` - Rendering utilities (Graphics, Antialiasing, RenderEngine)
- `input/hotkey_listener.py` - `HotkeyListener`: Global hotkey listener using `keyboard` library
- `input/controller.py` - `ModeController`: Bridges between hotkey events and disk UI mode switching
- `system/app.py` - `WheelToolApp`: Main application lifecycle manager
- `system/tray_icon.py` - `TrayIcon`: System tray integration
- `config/settings.py` - `GlobalConfig`: Application-level settings (window size, alpha, display timing)

### Data Flow

1. **Initialization** (`main.py`):
   - Creates `ModeManager` (loads mappings from `key_mappings.json`)
   - Creates `WheelDisk` (loads display config from `wheel_tool_config.json`)
   - Creates `ModeController` (links disk to mode switching logic)
   - Creates `HotkeyListener` (registers global hotkeys, links to disk and mode_manager)
   - Creates `WheelToolApp` (orchestrates all components)

2. **Mode Switching**:
   - User presses `Ctrl+Alt+Shift+-` (next) or `Ctrl+Alt+Shift+=` (prev)
   - `HotkeyListener` captures hotkey → calls `disk.next_mode()` or `disk.prev_mode()`
   - `WheelDisk` updates `current_mode` index → redraws disk with new colors
   - Display auto-hides after configurable delay

3. **Key Mapping Execution**:
   - User presses mapped key (e.g., `f13` in 浏览模式)
   - `HotkeyListener._handle_mapped_key()` checks if key is mapped in current mode
   - If mapped: mode executes `_press_key()` with target key combo (e.g., `ctrl+w`)
   - If `block=true`: source key is suppressed

4. **Configuration Persistence**:
   - Key mappings: `ModeManager.save_config()` → `key_mappings.json`
   - App settings: `GlobalConfig.save()` → `wheel_tool_config.json`

## Configuration Files

### `key_mappings.json`
Defines key mappings per mode. Structure:
```json
{
  "浏览模式": {
    "enabled": true,
    "mappings": [
      {
        "source": "f13",
        "target": "control_l+w",
        "block": true,
        "hint": "关闭"
      }
    ]
  }
}
```

### `wheel_tool_config.json`
Application display and behavior settings:
```json
{
  "window": {
    "alpha": 1.0,
    "size": 320,
    "center_on_screen": true
  },
  "display": {
    "fade_step": 25,
    "hide_delay": 800
  },
  "hotkeys": {
    "next_mode": "ctrl+alt+shift+-",
    "prev_mode": "ctrl+alt+shift+=",
    "open_settings": "ctrl+alt+shift+s",
    "hide_disk": "esc"
  }
}
```

## Key Technical Details

### WheelDisk Rendering (wheel_tool/ui/disk.py)
- Uses PIL to render at 4x scale (`self.scale = 4`) then downscale with LANCZOS for antialiasing
- Disk is divided into 4 sectors (90° each) representing the 4 modes
- Active mode gets gradient colors from `self.COLORS`, inactive modes are gray
- Text overlay drawn separately after scaling to avoid font distortion
- Auto-hide timer resets on mode switch to keep disk visible during interaction

### Hotkey System (wheel_tool/input/hotkey_listener.py)
- Uses `keyboard` library for cross-platform global hotkey hooking
- `_register_mapped_keys()` registers all source keys from all modes with `suppress=True`
- When key pressed, checks current mode and executes mapping if exists
- Supports modifier key detection (Ctrl, Alt, Shift) to preserve combo keys

### Mode Management (key_mapper/core/manager.py)
- Maintains list of mode instances (BrowseMode, MediaMode, etc.)
- Each mode inherits from `BaseMode` and defines `get_default_mappings()`
- `execute_mapping()` uses `pynput.keyboard.Controller` to simulate target keypresses
- Key parsing supports special keys (arrows, F-keys, modifiers) and combinations

### Application Lifecycle (wheel_tool/system/app.py)
- `WheelToolApp` coordinates all components and handles cleanup
- Tray icon provides pause/resume (disables hotkey mappings without exiting)
- Signal handlers for graceful shutdown (saves config on exit)
- Restart functionality spawns new process and exits current one

## Common Development Patterns

### Adding a New Mode
1. Create mode class in `key_mapper/core/modes.py` inheriting from `BaseMode`
2. Implement `get_default_mappings()` returning list of (source, target) tuples
3. Add to `ModeManager.__init__()` in `key_mapper/core/manager.py`
4. Add mode name to `WheelDisk.MODES` and color scheme to `WheelDisk.COLORS` in `wheel_tool/ui/disk.py`

### Modifying Key Mappings Programmatically
```python
mode_manager = ModeManager()
browse_mode = mode_manager.get_mode_by_name("浏览模式")
browse_mode.add_mapping("f18", "ctrl+t", block=True, hint="新标签")
mode_manager.save_config()
```

### Changing Display Timing
```python
GlobalConfig.set('display.hide_delay', 1000)  # milliseconds
GlobalConfig.save()
```

## Important Notes

- **Administrator Rights Required**: Global keyboard hooking requires elevated permissions on Windows
- **Threading Model**: UI runs on main thread (tkinter), hotkey listener runs on separate thread via `keyboard` library
- **Key Names**: Use lowercase with underscores for special keys (e.g., `control_l`, `shift_r`, `alt_l`) in mappings
- **Mode Synchronization**: `HotkeyListener` syncs mode index from `WheelDisk.current_mode` to `ModeManager.current_index` on each key event
- **PIL Required**: Wheel disk rendering requires Pillow for antialiased graphics
- **Font Path**: Disk text uses `msyh.ttc` (Microsoft YaHei) - falls back to default if not found
- 用中文回复用户
- 代码注释也使用中文