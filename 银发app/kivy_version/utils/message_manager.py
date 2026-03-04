"""
消息提示管理器 - 用于显示全局消息提示
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.animation import Animation

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from styles import get_color, get_font_size, DIMENSIONS


class MessageToast(BoxLayout):
    """消息提示组件"""
    
    def __init__(self, message, msg_type='info', duration=3, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.size = (400, 60)
        self.padding = (15, 10)
        self.spacing = 10
        
        # 根据类型设置颜色
        colors = {
            'info': get_color('primary'),
            'success': get_color('success'),
            'warning': get_color('warning'),
            'error': get_color('danger')
        }
        self.bg_color = colors.get(msg_type, get_color('primary'))
        
        # 设置背景
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos,
                                        radius=[DIMENSIONS['card_radius']])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # 图标
        icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        icon = Label(
            text=icons.get(msg_type, 'ℹ️'),
            font_size=24,
            size_hint=(0.15, 1)
        )
        self.add_widget(icon)
        
        # 消息文本
        msg_label = Label(
            text=message,
            font_size=get_font_size('body'),
            color=get_color('text_light'),
            size_hint=(0.85, 1),
            halign='left',
            valign='center'
        )
        msg_label.bind(size=msg_label.setter('text_size'))
        self.add_widget(msg_label)
        
        # 自动消失
        Clock.schedule_once(self.dismiss, duration)
    
    def update_rect(self, instance, value):
        """更新矩形位置和大小"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def dismiss(self, dt=None):
        """消失动画"""
        anim = Animation(opacity=0, duration=0.3)
        anim.bind(on_complete=lambda x, y: self.parent.remove_widget(self) if self.parent else None)
        anim.start(self)


class MessageManager:
    """消息管理器 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.toasts = []
            cls._instance.max_toasts = 3
        return cls._instance
    
    def show(self, message, msg_type='info', duration=3):
        """显示消息提示
        
        Args:
            message: 消息内容
            msg_type: 消息类型 (info/success/warning/error)
            duration: 显示时长（秒）
        """
        # 获取根窗口
        from kivy.app import App
        app = App.get_running_app()
        if not app or not app.root:
            return
        
        # 创建消息提示
        toast = MessageToast(message, msg_type, duration)
        
        # 添加到窗口
        app.root.add_widget(toast)
        
        # 设置位置（屏幕底部居中）
        toast.center_x = app.root.center_x
        toast.y = 100 + len(self.toasts) * 70
        
        # 限制最大数量
        self.toasts.append(toast)
        if len(self.toasts) > self.max_toasts:
            old_toast = self.toasts.pop(0)
            if old_toast.parent:
                old_toast.parent.remove_widget(old_toast)
    
    def info(self, message, duration=3):
        """显示信息消息"""
        self.show(message, 'info', duration)
    
    def success(self, message, duration=3):
        """显示成功消息"""
        self.show(message, 'success', duration)
    
    def warning(self, message, duration=3):
        """显示警告消息"""
        self.show(message, 'warning', duration)
    
    def error(self, message, duration=3):
        """显示错误消息"""
        self.show(message, 'error', duration)


# 全局消息管理器实例
message_manager = MessageManager()


def show_message(message, msg_type='info', duration=3):
    """便捷函数：显示消息提示"""
    message_manager.show(message, msg_type, duration)


def show_info(message, duration=3):
    """便捷函数：显示信息"""
    message_manager.info(message, duration)


def show_success(message, duration=3):
    """便捷函数：显示成功消息"""
    message_manager.success(message, duration)


def show_warning(message, duration=3):
    """便捷函数：显示警告"""
    message_manager.warning(message, duration)


def show_error(message, duration=3):
    """便捷函数：显示错误"""
    message_manager.error(message, duration)
