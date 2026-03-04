"""
管理员登录页面 - 使用统一UI样式
支持登录和注册功能
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import random
import string
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from screens.base_screen import BaseScreen
from styles import get_color, get_font_size, DIMENSIONS


class AdminLoginScreen(BaseScreen):
    name = StringProperty('admin_login')

    def __init__(self, voice_engine, db_manager, app, **kwargs):
        self.title = '管理员登录'
        super().__init__(voice_engine, app, **kwargs)
        self.db_manager = db_manager
        self.mode = 'login'  # 'login' or 'register'
        self.captcha_code = ''

        self.build_ui()
        Clock.schedule_once(lambda dt: self.refresh_captcha(), 0.5)

    def build_ui(self):
        """构建管理员登录界面"""
        super().build_ui()

        content = BoxLayout(orientation='vertical', spacing=20, padding=30)

        # 登录表单卡片
        form_card = self.create_card(orientation='vertical', size_hint=(1, 0.75),
                                     padding=25, spacing=15)

        # 标题
        self.form_title = Label(
            text='管理员登录',
            font_size=get_font_size('title'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=50
        )
        form_card.add_widget(self.form_title)

        # 用户名输入
        username_label = Label(
            text='用户名',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=25,
            halign='left'
        )
        username_label.bind(size=username_label.setter('text_size'))
        form_card.add_widget(username_label)

        self.username_input = TextInput(
            hint_text='请输入用户名',
            font_size=get_font_size('body'),
            size_hint=(1, None),
            height=50,
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[15, 15]
        )
        form_card.add_widget(self.username_input)

        # 密码输入
        password_label = Label(
            text='密码',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=25,
            halign='left'
        )
        password_label.bind(size=password_label.setter('text_size'))
        form_card.add_widget(password_label)

        self.password_input = TextInput(
            hint_text='请输入密码',
            font_size=get_font_size('body'),
            size_hint=(1, None),
            height=50,
            multiline=False,
            password=True,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[15, 15]
        )
        form_card.add_widget(self.password_input)

        # 确认密码（仅注册模式显示）
        self.confirm_password_label = Label(
            text='确认密码',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=25,
            halign='left'
        )
        self.confirm_password_label.bind(size=self.confirm_password_label.setter('text_size'))
        self.confirm_password_label.opacity = 0
        form_card.add_widget(self.confirm_password_label)

        self.confirm_password_input = TextInput(
            hint_text='请再次输入密码',
            font_size=get_font_size('body'),
            size_hint=(1, None),
            height=50,
            multiline=False,
            password=True,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[15, 15],
            opacity=0
        )
        form_card.add_widget(self.confirm_password_input)

        # 验证码
        captcha_layout = BoxLayout(orientation='horizontal', size_hint=(1, None),
                                   height=50, spacing=10)

        self.captcha_input = TextInput(
            hint_text='验证码',
            font_size=get_font_size('body'),
            size_hint=(0.5, 1),
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[15, 15]
        )
        captcha_layout.add_widget(self.captcha_input)

        # 验证码显示
        self.captcha_label = Label(
            text='',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(0.3, 1)
        )
        captcha_layout.add_widget(self.captcha_label)

        # 刷新按钮
        refresh_btn = self.create_button(
            text='刷新',
            color_key='secondary',
            size_hint=(0.2, 1),
            on_press=lambda x: self.refresh_captcha()
        )
        captcha_layout.add_widget(refresh_btn)

        form_card.add_widget(captcha_layout)

        # 登录/注册按钮
        self.action_btn = self.create_button(
            text='登录',
            color_key='success',
            size_hint=(1, None),
            height=55,
            on_press=self.handle_action
        )
        form_card.add_widget(self.action_btn)

        # 切换模式按钮
        self.switch_btn = self.create_button(
            text='还没有账号？去注册',
            color_key='secondary',
            size_hint=(1, None),
            height=45,
            on_press=self.switch_mode
        )
        form_card.add_widget(self.switch_btn)

        content.add_widget(form_card)

        # 提示信息
        tip_card = self.create_card(orientation='vertical', size_hint=(1, None),
                                    height=100, padding=15)

        tip_label = Label(
            text='提示：管理员账号用于管理系统用户、\n订单和发布社区通知。',
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, 1)
        )
        tip_card.add_widget(tip_label)
        content.add_widget(tip_card)

        self.content_area.add_widget(content)

    def refresh_captcha(self):
        """刷新验证码"""
        self.captcha_code = ''.join(random.choices(string.digits, k=4))
        self.captcha_label.text = self.captcha_code

    def switch_mode(self, instance=None):
        """切换登录/注册模式"""
        if self.mode == 'login':
            self.mode = 'register'
            self.form_title.text = '管理员注册'
            self.action_btn.text = '注册'
            self.switch_btn.text = '已有账号？去登录'
            self.confirm_password_label.opacity = 1
            self.confirm_password_input.opacity = 1
            self.confirm_password_input.disabled = False
            if self.voice_engine:
                self.voice_engine.speak('切换到注册模式')
        else:
            self.mode = 'login'
            self.form_title.text = '管理员登录'
            self.action_btn.text = '登录'
            self.switch_btn.text = '还没有账号？去注册'
            self.confirm_password_label.opacity = 0
            self.confirm_password_input.opacity = 0
            self.confirm_password_input.disabled = True
            if self.voice_engine:
                self.voice_engine.speak('切换到登录模式')
        
        self.refresh_captcha()

    def handle_action(self, instance=None):
        """处理登录/注册"""
        if self.mode == 'login':
            self.login()
        else:
            self.register()

    def login(self):
        """登录"""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        captcha = self.captcha_input.text.strip()

        if not username or not password:
            self.show_message('请输入用户名和密码', 'warning')
            if self.voice_engine:
                self.voice_engine.speak("请输入用户名和密码")
            return

        if captcha.upper() != self.captcha_code.upper():
            self.show_message('验证码错误', 'error')
            if self.voice_engine:
                self.voice_engine.speak("验证码错误")
            self.refresh_captcha()
            return

        # 验证管理员账号
        if self.db_manager:
            admin = self.db_manager.verify_admin(username, password)
            if admin:
                self.show_message('登录成功', 'success')
                if self.voice_engine:
                    self.voice_engine.speak("登录成功")
                self.clear_inputs()
                self.app.show_screen('admin')
                return
        
        # 默认管理员账号（用于测试）
        if username == 'admin' and password == 'admin123':
            self.show_message('登录成功', 'success')
            if self.voice_engine:
                self.voice_engine.speak("登录成功")
            self.clear_inputs()
            self.app.show_screen('admin')
        else:
            self.show_message('用户名或密码错误', 'error')
            if self.voice_engine:
                self.voice_engine.speak("用户名或密码错误")
            self.refresh_captcha()

    def register(self):
        """注册"""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()
        captcha = self.captcha_input.text.strip()

        if not username or not password:
            self.show_message('请输入用户名和密码', 'warning')
            if self.voice_engine:
                self.voice_engine.speak("请输入用户名和密码")
            return

        if password != confirm_password:
            self.show_message('两次输入的密码不一致', 'error')
            if self.voice_engine:
                self.voice_engine.speak("两次输入的密码不一致")
            return

        if captcha.upper() != self.captcha_code.upper():
            self.show_message('验证码错误', 'error')
            if self.voice_engine:
                self.voice_engine.speak("验证码错误")
            self.refresh_captcha()
            return

        # 注册管理员账号
        if self.db_manager:
            success = self.db_manager.register_admin(username, password)
            if success:
                self.show_message('注册成功', 'success')
                if self.voice_engine:
                    self.voice_engine.speak("注册成功，请登录")
                self.switch_mode()
            else:
                self.show_message('用户名已存在', 'error')
                if self.voice_engine:
                    self.voice_engine.speak("用户名已存在")
        else:
            self.show_message('注册成功', 'success')
            if self.voice_engine:
                self.voice_engine.speak("注册成功，请登录")
            self.switch_mode()

    def clear_inputs(self):
        """清空输入框"""
        self.username_input.text = ''
        self.password_input.text = ''
        self.confirm_password_input.text = ''
        self.captcha_input.text = ''

    def show_message(self, message, msg_type='info'):
        """显示消息弹窗"""
        colors = {
            'info': get_color('primary'),
            'success': get_color('success'),
            'warning': get_color('warning'),
            'error': get_color('danger')
        }
        
        popup = Popup(
            title='提示',
            content=Label(
                text=message,
                font_size=get_font_size('body'),
                color=colors.get(msg_type, get_color('text_primary'))
            ),
            size_hint=(0.8, 0.3),
            auto_dismiss=True
        )
        popup.open()
        
        # 3秒后自动关闭
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
