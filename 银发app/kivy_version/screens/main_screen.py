from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
from kivy.core.text import LabelBase
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入样式
from styles import get_color, get_button_color, get_font_size, get_icon, DIMENSIONS


class RoundedButton(Button):
    """圆角按钮"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[DIMENSIONS['button_radius']])


class MainScreen(Screen):
    name = StringProperty('main')
    
    def __init__(self, voice_engine, ai_assistant, community_service, 
                 meal_service, payment_service, entertainment_service,
                 db_manager, app, **kwargs):
        super().__init__(**kwargs)
        self.voice_engine = voice_engine
        self.ai_assistant = ai_assistant
        self.community_service = community_service
        self.meal_service = meal_service
        self.payment_service = payment_service
        self.entertainment_service = entertainment_service
        self.db_manager = db_manager
        self.app = app
        
        self.build_ui()
    
    def build_ui(self):
        """构建主界面"""
        # 主布局 - 米白背景
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        with main_layout.canvas.before:
            Color(*get_color('background'))
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self.update_bg, pos=self.update_bg)
        
        # 顶部标题栏 - 温暖橙色
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.12), padding=[0, 10, 0, 10])
        with header.canvas.before:
            Color(*get_color('primary'))
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self.update_header, pos=self.update_header)
        
        title_label = Label(
            text=f"{get_icon('')} 银发关爱",
            font_size=get_font_size('title'),
            bold=True,
            color=get_color('text_light'),
            size_hint=(1, 0.6)
        )
        
        subtitle_label = Label(
            text='智慧养老服务平台',
            font_size=get_font_size('caption'),
            color=(1, 1, 1, 0.9),
            size_hint=(1, 0.4)
        )
        
        header.add_widget(title_label)
        header.add_widget(subtitle_label)
        main_layout.add_widget(header)
        
        # 欢迎卡片
        welcome_card = BoxLayout(orientation='vertical', size_hint=(1, 0.1), 
                                  padding=[20, 15], spacing=5)
        with welcome_card.canvas.before:
            Color(*get_color('card'))
            self.welcome_rect = RoundedRectangle(size=welcome_card.size, pos=welcome_card.pos, 
                                                  radius=[DIMENSIONS['card_radius']])
        welcome_card.bind(size=self.update_welcome_card, pos=self.update_welcome_card)
        
        welcome_text = Label(
            text='欢迎您，请选择所需服务',
            font_size=get_font_size('body'),
            color=get_color('text_primary'),
            halign='left',
            valign='center'
        )
        welcome_text.bind(size=welcome_text.setter('text_size'))
        welcome_card.add_widget(welcome_text)
        
        main_layout.add_widget(welcome_card)
        
        # 功能按钮网格
        grid_container = BoxLayout(orientation='vertical', size_hint=(1, 0.68), 
                                    padding=[15, 10, 15, 10])
        
        grid_layout = GridLayout(cols=3, spacing=DIMENSIONS['spacing'], 
                                  size_hint=(1, 1))
        
        # 功能按钮配置
        buttons = [
            {'text': '订餐服务', 'screen': 'meal', 'icon': '🍽️'},
            {'text': '缴费服务', 'screen': 'payment', 'icon': '💳'},
            {'text': '健康记录', 'screen': 'health', 'icon': '❤️'},
            {'text': '娱乐中心', 'screen': 'entertainment', 'icon': '🎮'},
            {'text': '社区通知', 'screen': 'notification', 'icon': '🔔'},
            {'text': 'AI助手', 'screen': 'ai_assistant', 'icon': '🤖'},
            {'text': '紧急呼叫', 'screen': 'emergency', 'icon': '🆘'},
            {'text': '计算器', 'screen': 'calculator', 'icon': '🧮'},
            {'text': '管理员', 'screen': 'admin_login', 'icon': '👤'},
        ]
        
        for btn_info in buttons:
            btn = self.create_service_button(
                text=btn_info['text'],
                icon=btn_info['icon'],
                screen=btn_info['screen']
            )
            grid_layout.add_widget(btn)
        
        grid_container.add_widget(grid_layout)
        main_layout.add_widget(grid_container)
        
        # 底部状态栏
        footer = BoxLayout(orientation='horizontal', size_hint=(1, 0.06), 
                           padding=[15, 5])
        with footer.canvas.before:
            Color(*get_color('divider'))
            self.footer_rect = Rectangle(size=footer.size, pos=footer.pos)
        footer.bind(size=self.update_footer, pos=self.update_footer)
        
        footer_text = Label(
            text='📱 银发关爱 v1.0 | 让养老更智能',
            font_size=14,
            color=get_color('text_secondary'),
            halign='center'
        )
        footer.add_widget(footer_text)
        main_layout.add_widget(footer)
        
        self.add_widget(main_layout)
    
    def create_service_button(self, text, icon, screen):
        """创建服务按钮"""
        btn_layout = BoxLayout(orientation='vertical', spacing=5)
        
        # 按钮背景
        btn_color = get_button_color(screen)
        with btn_layout.canvas.before:
            Color(*btn_color)
            self.btn_rect = RoundedRectangle(size=btn_layout.size, pos=btn_layout.pos,
                                              radius=[DIMENSIONS['card_radius']])
        btn_layout.bind(size=self.update_btn_rect, pos=self.update_btn_rect)
        
        # 文字
        text_label = Label(
            text=text,
            font_size=get_font_size('button'),
            bold=True,
            size_hint=(1, 1),
            color=get_color('text_light')
        )
        
        btn_layout.add_widget(text_label)
        
        # 绑定点击事件
        btn_layout.bind(on_touch_down=lambda instance, touch, s=screen: 
                        self.on_button_press(s) if instance.collide_point(*touch.pos) else None)
        
        return btn_layout
    
    def update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    def update_header(self, instance, value):
        self.header_rect.size = instance.size
        self.header_rect.pos = instance.pos
    
    def update_welcome_card(self, instance, value):
        self.welcome_rect.size = instance.size
        self.welcome_rect.pos = instance.pos
    
    def update_footer(self, instance, value):
        self.footer_rect.size = instance.size
        self.footer_rect.pos = instance.pos
    
    def update_btn_rect(self, instance, value):
        # 更新按钮背景
        instance.canvas.before.clear()
        with instance.canvas.before:
            # 获取按钮对应的颜色
            screen_name = instance.screen if hasattr(instance, 'screen') else 'meal'
            Color(*get_button_color(screen_name))
            RoundedRectangle(size=instance.size, pos=instance.pos,
                            radius=[DIMENSIONS['card_radius']])
    
    def on_button_press(self, screen_name):
        """按钮点击事件"""
        if screen_name == 'emergency':
            self.voice_engine.speak("正在呼叫紧急联系人")
        self.app.show_screen(screen_name)
