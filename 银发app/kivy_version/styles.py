"""
银发关爱APP - 样式配置
专为老年人设计的温暖、简洁、易读的界面风格
"""

# 主色调 - 平和的白蓝配色
COLORS = {
    'primary': (0.25, 0.55, 0.85, 1),      # 平和蓝 #4A90D9
    'primary_light': (0.45, 0.70, 0.95, 1), # 浅蓝 #73B3F2
    'primary_dark': (0.15, 0.40, 0.70, 1), # 深蓝 #2666B3
    
    'secondary': (0.50, 0.75, 0.90, 1),    # 天蓝 #80BFE6
    'secondary_light': (0.70, 0.88, 0.98, 1), # 淡蓝 #B3E0FA
    
    'success': (0.40, 0.70, 0.50, 1),      # 柔和绿 #66B380
    'warning': (0.95, 0.75, 0.35, 1),      # 柔和黄 #F2BF5A
    'danger': (0.85, 0.45, 0.45, 1),       # 柔和红 #D97373
    
    'background': (0.97, 0.98, 1.00, 1),   # 淡蓝白背景 #F7F9FF
    'card': (1, 1, 1, 1),                  # 纯白卡片 #FFFFFF
    'text_primary': (0.25, 0.30, 0.40, 1), # 深蓝灰文字 #404D66
    'text_secondary': (0.50, 0.55, 0.65, 1), # 次要文字 #808BA6
    'text_light': (1, 1, 1, 1),            # 浅色文字 #FFFFFF
    
    'divider': (0.88, 0.90, 0.95, 1),      # 淡蓝分隔线 #E0E6F2
    'shadow': (0.20, 0.25, 0.35, 0.08),    # 淡阴影
}

# 功能按钮配色 - 柔和蓝调
BUTTON_COLORS = {
    'meal': (0.35, 0.60, 0.85, 1),         # 订餐 - 柔和蓝
    'payment': (0.40, 0.65, 0.88, 1),      # 缴费 - 天蓝
    'health': (0.45, 0.75, 0.65, 1),       # 健康 - 柔和绿
    'entertainment': (0.55, 0.60, 0.85, 1), # 娱乐 - 淡紫蓝
    'notification': (0.50, 0.70, 0.90, 1), # 通知 - 浅蓝
    'ai_assistant': (0.60, 0.65, 0.75, 1), # AI助手 - 灰蓝
    'emergency': (0.85, 0.50, 0.50, 1),    # 紧急 - 柔和红
    'voice_settings': (0.65, 0.70, 0.80, 1), # 设置 - 浅灰蓝
    'calculator': (0.50, 0.65, 0.85, 1),   # 计算器 - 蓝灰
}

# 字体大小（适合老年人阅读）
FONTS = {
    'title': 36,       # 大标题
    'subtitle': 28,    # 副标题
    'heading': 24,     # 小标题
    'body': 20,        # 正文
    'button': 22,      # 按钮文字
    'caption': 16,     # 说明文字
    'large': 26,       # 大按钮文字
    'display': 48,     # 计算器显示屏
}

# 尺寸
DIMENSIONS = {
    'button_height': 100,      # 按钮高度
    'button_height_large': 130, # 大按钮高度
    'card_padding': 15,        # 卡片内边距
    'card_radius': 15,         # 卡片圆角
    'button_radius': 12,       # 按钮圆角
    'spacing': 12,             # 间距
}

# 图标（使用Unicode字符作为简单图标）
ICONS = {
    'meal': '🍽️',
    'payment': '💳',
    'health': '❤️',
    'entertainment': '🎮',
    'notification': '🔔',
    'ai_assistant': '🤖',
    'emergency': '🆘',
    'voice_settings': '🔊',
    'back': '←',
    'send': '➤',
    'mic': '🎤',
    'clear': '✕',
}

def get_color(name):
    """获取颜色"""
    return COLORS.get(name, (0, 0, 0, 1))

def get_button_color(screen_name):
    """获取按钮颜色"""
    return BUTTON_COLORS.get(screen_name, COLORS['primary'])

def get_font_size(size_name):
    """获取字体大小"""
    return FONTS.get(size_name, 20)

def get_icon(icon_name):
    """获取图标"""
    return ICONS.get(icon_name, '')
