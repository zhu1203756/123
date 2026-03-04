"""
基础屏幕类 - 提供统一的UI样式和导航栏
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from styles import get_color, get_font_size, DIMENSIONS


class BaseScreen(Screen):
    """基础屏幕类，提供统一的UI样式"""
    
    title = StringProperty('')
    
    def __init__(self, voice_engine, app, **kwargs):
        super().__init__(**kwargs)
        self.voice_engine = voice_engine
        self.app = app
        self.main_layout = None
        self.content_area = None
        
    def build_ui(self):
        """构建UI框架"""
        # 主布局
        self.main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # 设置背景色
        with self.main_layout.canvas.before:
            Color(*get_color('background'))
            self.bg_rect = Rectangle(size=self.main_layout.size, pos=self.main_layout.pos)
        self.main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # 添加导航栏
        nav_bar = self._create_nav_bar()
        self.main_layout.add_widget(nav_bar)
        
        # 内容区域
        self.content_area = BoxLayout(orientation='vertical', size_hint=(1, 0.88))
        self.main_layout.add_widget(self.content_area)
        
        self.add_widget(self.main_layout)
        
    def _create_nav_bar(self):
        """创建统一导航栏"""
        nav_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.12), 
                           padding=[10, 10])
        
        with nav_bar.canvas.before:
            Color(*get_color('primary'))
            self.nav_rect = Rectangle(size=nav_bar.size, pos=nav_bar.pos)
        nav_bar.bind(size=self._update_nav, pos=self._update_nav)
        
        # 返回按钮
        back_btn = Label(
            text='← 返回',
            font_size=get_font_size('body'),
            color=get_color('text_light'),
            size_hint=(0.2, 1),
            halign='left'
        )
        back_btn.bind(on_touch_down=self._on_back_touch)
        nav_bar.add_widget(back_btn)
        
        # 标题
        title_label = Label(
            text=self.title,
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('text_light'),
            size_hint=(0.6, 1),
            halign='center'
        )
        nav_bar.add_widget(title_label)
        
        # 占位（保持对称）
        spacer = Label(size_hint=(0.2, 1))
        nav_bar.add_widget(spacer)
        
        return nav_bar
    
    def _on_back_touch(self, instance, touch):
        """处理返回按钮点击"""
        if instance.collide_point(*touch.pos):
            self.voice_engine.speak("返回主页面")
            self.app.show_screen('main')
            return True
        return False
    
    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    def _update_nav(self, instance, value):
        self.nav_rect.size = instance.size
        self.nav_rect.pos = instance.pos
    
    def create_card(self, **kwargs):
        """创建卡片容器"""
        if 'orientation' not in kwargs:
            kwargs['orientation'] = 'vertical'
        card = BoxLayout(**kwargs)
        with card.canvas.before:
            Color(*get_color('card'))
            self.card_rect = RoundedRectangle(size=card.size, pos=card.pos,
                                              radius=[DIMENSIONS['card_radius']])
        card.bind(size=self._update_card, pos=self._update_card)
        return card
    
    def _update_card(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*get_color('card'))
            RoundedRectangle(size=instance.size, pos=instance.pos,
                           radius=[DIMENSIONS['card_radius']])
    
    def create_button(self, text, color_key='primary', on_press=None, **kwargs):
        """创建统一风格的按钮"""
        from kivy.uix.button import Button
        from kivy.graphics import Color, RoundedRectangle
        
        # 创建标准按钮
        btn = Button(
            text=text,
            font_size=get_font_size('button'),
            bold=True,
            color=get_color('text_light'),
            background_color=get_color(color_key),
            background_normal='',
            **kwargs
        )
        
        # 添加圆角背景
        def update_bg(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*get_color(color_key))
                RoundedRectangle(size=instance.size, pos=instance.pos,
                               radius=[DIMENSIONS['button_radius']])
        
        btn.bind(size=update_bg, pos=update_bg)
        
        # 绑定点击事件
        if on_press:
            btn.bind(on_press=on_press)
        
        return btn
    
    def create_label(self, text, size='body', color='text_primary', **kwargs):
        """创建统一风格的标签"""
        return Label(
            text=text,
            font_size=get_font_size(size),
            color=get_color(color),
            **kwargs
        )
    
    def create_spinner(self, text, values, **kwargs):
        """创建统一风格的下拉菜单"""
        # 创建容器
        spinner_layout = BoxLayout(orientation='vertical', **kwargs)
        
        # 设置背景
        with spinner_layout.canvas.before:
            Color(*get_color('background'))
            RoundedRectangle(size=spinner_layout.size, pos=spinner_layout.pos,
                           radius=[DIMENSIONS['button_radius']])
        
        def update_spinner_bg(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*get_color('background'))
                RoundedRectangle(size=instance.size, pos=instance.pos,
                               radius=[DIMENSIONS['button_radius']])
        
        spinner_layout.bind(size=update_spinner_bg, pos=update_spinner_bg)
        
        # 创建Spinner
        from kivy.uix.spinner import Spinner
        spinner = Spinner(
            text=text,
            values=values,
            font_size=get_font_size('body'),
            size_hint=(1, 1),
            background_color=(0, 0, 0, 0),  # 透明背景
            color=get_color('text_primary')
        )
        
        # 为下拉菜单设置样式
        spinner.background_normal = ''
        spinner.background_down = ''
        
        spinner_layout.add_widget(spinner)
        return spinner, spinner_layout
