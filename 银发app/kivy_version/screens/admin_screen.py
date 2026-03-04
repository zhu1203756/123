from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp
from styles import get_color, get_font_size, DIMENSIONS
import random
import string
from database import get_db_connection, close_db_connection


class RoundedTextInput(TextInput):
    """圆角输入框"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 保留默认背景，通过canvas在上面绘制圆角背景
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (1, 1, 1, 0.9)
        self.cursor_color = get_color('primary')
        self.foreground_color = (0, 0, 0, 1)
        self.padding = [dp(15), dp(12)]
        self.disabled = False
        self.focus = True
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        # 先清除canvas
        self.canvas.before.clear()
        # 绘制背景
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])


class GradientButton(Button):
    """渐变按钮"""
    def __init__(self, bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.bg_color = bg_color or get_color('primary')
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(25)])


class AdminLoginScreen(Screen):
    """管理员登录页面"""
    name = StringProperty('admin_login')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # 根布局
        root = FloatLayout()
        
        # 背景渐变
        with root.canvas.before:
            Color(0.94, 0.95, 0.98, 1)
            Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)
        
        # 主卡片 - 调整高度和间距
        card = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10),
            size_hint=(0.92, 0.88),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(20)])
        card.bind(pos=self.update_card, size=self.update_card)
        
        # 标题区域 - 调整为水平布局，确保标题显示完整
        title_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80))
        
        # 标题（居中显示）
        title_label = Label(
            text='管理员登录',
            font_size=dp(24),
            bold=True,
            color=get_color('text_primary'),
            halign='center',
            valign='middle'
        )
        title_box.add_widget(title_label)
        
        card.add_widget(title_box)
        
        # 表单区域 - 减小间距
        form_box = BoxLayout(orientation='vertical', spacing=dp(12))
        
        # 账号标签
        username_label = Label(
            text='账 号',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        username_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(username_label)
        
        # 账号输入
        self.username_input = TextInput(
            hint_text='请输入管理员账号',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        form_box.add_widget(self.username_input)
        
        # 密码标签
        password_label = Label(
            text='密 码',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        password_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(password_label)
        
        # 密码输入
        self.password_input = TextInput(
            hint_text='请输入密码',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            password=True,
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        form_box.add_widget(self.password_input)
        
        # 验证码标签
        captcha_label = Label(
            text='验 证 码',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        captcha_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(captcha_label)
        
        # 验证码区域
        captcha_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
        
        self.code_input = TextInput(
            hint_text='请输入验证码',
            font_size=dp(15),
            size_hint_x=0.55,
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        captcha_box.add_widget(self.code_input)
        
        # 验证码显示
        self.captcha_code = self.generate_captcha()
        captcha_bg = BoxLayout(size_hint_x=0.45)
        with captcha_bg.canvas.before:
            Color(0.94, 0.96, 0.98, 1)
            self.captcha_rect = RoundedRectangle(pos=captcha_bg.pos, size=captcha_bg.size, radius=[dp(10)])
        captcha_bg.bind(pos=self.update_captcha_bg, size=self.update_captcha_bg)
        
        self.captcha_label = Label(
            text=self.captcha_code,
            font_size=dp(20),
            bold=True,
            color=(0.25, 0.45, 0.65, 1)
        )
        captcha_bg.add_widget(self.captcha_label)
        captcha_box.add_widget(captcha_bg)
        
        form_box.add_widget(captcha_box)
        
        # 刷新验证码按钮
        refresh_btn = Button(
            text='看不清？点击刷新',
            font_size=dp(12),
            size_hint_y=None,
            height=dp(28),
            background_color=(0, 0, 0, 0),
            color=get_color('secondary'),
            background_normal=''
        )
        refresh_btn.bind(on_press=self.refresh_captcha)
        form_box.add_widget(refresh_btn)
        
        card.add_widget(form_box)
        
        # 按钮区域
        btn_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(140))
        
        # 登录按钮
        login_btn = GradientButton(
            text='登 录',
            font_size=dp(17),
            bold=True,
            bg_color=get_color('primary'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(48)
        )
        login_btn.bind(on_press=self.login)
        btn_box.add_widget(login_btn)
        
        # 注册按钮
        register_btn = GradientButton(
            text='注 册 新 账 号',
            font_size=dp(15),
            bg_color=(0.4, 0.7, 0.4, 1),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(42)
        )
        register_btn.bind(on_press=self.go_to_register)
        btn_box.add_widget(register_btn)
        
        # 返回按钮
        back_btn = Button(
            text='← 返回首页',
            font_size=dp(14),
            background_color=(0, 0, 0, 0),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(35)
        )
        back_btn.bind(on_press=self.go_back)
        btn_box.add_widget(back_btn)
        
        card.add_widget(btn_box)
        
        root.add_widget(card)
        self.add_widget(root)
    
    def update_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.98, 0.98, 1, 1)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def update_card(self, instance, value):
        self.card_rect.pos = instance.pos
        self.card_rect.size = instance.size
    
    def update_captcha_bg(self, instance, value):
        self.captcha_rect.pos = instance.pos
        self.captcha_rect.size = instance.size
    
    def generate_captcha(self):
        """生成随机验证码"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    
    def refresh_captcha(self, instance):
        """刷新验证码"""
        self.captcha_code = self.generate_captcha()
        self.captcha_label.text = self.captcha_code
    
    def login(self, instance):
        """登录验证"""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        code = self.code_input.text.strip().upper()
        
        # 验证验证码（不区分大小写）
        if code != self.captcha_code.upper():
            self.show_popup('错误', '验证码错误')
            self.refresh_captcha(instance)
            return
        
        # 验证账号密码
        if self.validate_admin(username, password):
            # 登录成功，进入管理员页面
            self.manager.current = 'admin_main'
        else:
            self.show_popup('错误', '账号或密码错误')
    
    def validate_admin(self, username, password):
        """验证管理员账号密码"""
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM admins WHERE username=? AND password=?', (username, password))
                result = cursor.fetchone()
                close_db_connection(conn)
                return result is not None
            return False
        except Exception as e:
            print(f"验证管理员失败: {e}")
            return False
    
    def go_to_register(self, instance):
        """跳转到注册页面"""
        self.manager.current = 'admin_register'
    
    def go_back(self, instance):
        """返回上一页"""
        self.manager.current = 'main'
    
    def show_popup(self, title, message):
        """显示弹窗"""
        # 创建弹窗内容布局
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # 消息标签
        message_label = Label(
            text=message,
            font_size=dp(16),
            color=(0, 0, 0, 1),  # 黑色文字
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(message_label)
        
        # 确定按钮
        ok_button = GradientButton(
            text='确定',
            font_size=dp(16),
            bold=True,
            bg_color=get_color('primary'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(ok_button)
        
        # 创建弹窗
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False,
            title_size=dp(18),
            title_align='center',
            separator_height=dp(2),
            separator_color=get_color('primary'),
            background=''
        )
        
        # 直接设置弹窗背景为白色
        popup.canvas.before.clear()
        with popup.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(pos=popup.pos, size=popup.size)
        
        # 绑定位置和大小变化
        def update_bg(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(1, 1, 1, 1)
                Rectangle(pos=instance.pos, size=instance.size)
        
        popup.bind(pos=update_bg)
        popup.bind(size=update_bg)
        
        # 绑定确定按钮事件
        ok_button.bind(on_press=popup.dismiss)
        
        popup.open()


class AdminRegisterScreen(Screen):
    """管理员注册页面"""
    name = StringProperty('admin_register')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # 根布局
        root = FloatLayout()
        
        # 背景渐变
        with root.canvas.before:
            Color(0.94, 0.95, 0.98, 1)
            Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)
        
        # 主卡片 - 调整高度和间距
        card = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10),
            size_hint=(0.92, 0.88),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(20)])
        card.bind(pos=self.update_card, size=self.update_card)
        
        # 标题区域 - 调整为水平布局，确保标题显示完整
        title_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80))
        
        # 标题（居中显示）
        title_label = Label(
            text='管理员注册',
            font_size=dp(24),
            bold=True,
            color=get_color('text_primary'),
            halign='center',
            valign='middle'
        )
        title_box.add_widget(title_label)
        
        card.add_widget(title_box)
        
        # 表单区域 - 减小间距
        form_box = BoxLayout(orientation='vertical', spacing=dp(12))
        
        # 账号标签
        username_label = Label(
            text='账 号',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        username_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(username_label)
        
        # 账号输入
        self.username_input = TextInput(
            hint_text='请输入账号（只能用英文）',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        form_box.add_widget(self.username_input)
        
        # 密码标签
        password_label = Label(
            text='密 码',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        password_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(password_label)
        
        # 密码输入
        self.password_input = TextInput(
            hint_text='请输入密码（6-12位）',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            password=True,
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        form_box.add_widget(self.password_input)
        
        # 确认密码标签
        confirm_password_label = Label(
            text='确认密码',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        confirm_password_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(confirm_password_label)
        
        # 确认密码输入
        self.confirm_password_input = TextInput(
            hint_text='请确认密码',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            password=True,
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        form_box.add_widget(self.confirm_password_input)
        
        card.add_widget(form_box)
        
        # 按钮区域
        btn_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(140))
        
        # 注册按钮
        register_btn = GradientButton(
            text='注 册',
            font_size=dp(17),
            bold=True,
            bg_color=get_color('success'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(48)
        )
        register_btn.bind(on_press=self.register)
        btn_box.add_widget(register_btn)
        
        # 取消按钮
        cancel_btn = GradientButton(
            text='取 消',
            font_size=dp(15),
            bg_color=get_color('danger'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(42)
        )
        cancel_btn.bind(on_press=self.go_back)
        btn_box.add_widget(cancel_btn)
        
        # 返回按钮
        back_btn = Button(
            text='← 返回登录',
            font_size=dp(14),
            background_color=(0, 0, 0, 0),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(35)
        )
        back_btn.bind(on_press=self.go_back)
        btn_box.add_widget(back_btn)
        
        card.add_widget(btn_box)
        
        root.add_widget(card)
        self.add_widget(root)
    
    def update_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.98, 0.98, 1, 1)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def update_card(self, instance, value):
        self.card_rect.pos = instance.pos
        self.card_rect.size = instance.size
    
    def register(self, instance):
        """注册管理员账号"""
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()
        
        # 验证输入
        if not username.isalpha():
            self.show_popup('错误', '账号只能使用英文')
            return
        
        if len(password) < 6 or len(password) > 12:
            self.show_popup('错误', '密码长度必须在6-12位之间')
            return
        
        if password != confirm_password:
            self.show_popup('错误', '两次输入的密码不一致')
            return
        
        # 检查账号是否已存在
        if self.check_username_exists(username):
            self.show_popup('错误', '账号已存在')
            return
        
        # 注册账号
        if self.create_admin(username, password):
            self.show_popup('成功', '注册成功，请登录')
            self.manager.current = 'admin_login'
        else:
            self.show_popup('错误', '注册失败，请重试')
    
    def check_username_exists(self, username):
        """检查账号是否已存在"""
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM admins WHERE username=?', (username,))
                result = cursor.fetchone()
                close_db_connection(conn)
                return result is not None
            return False
        except Exception as e:
            print(f"检查账号失败: {e}")
            return False
    
    def create_admin(self, username, password):
        """创建管理员账号"""
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO admins (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                close_db_connection(conn)
                return True
            return False
        except Exception as e:
            print(f"创建管理员失败: {e}")
            return False
    
    def go_back(self, instance):
        """返回登录页面"""
        self.manager.current = 'admin_login'
    
    def show_popup(self, title, message):
        """显示弹窗"""
        # 创建弹窗内容布局
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # 消息标签
        message_label = Label(
            text=message,
            font_size=dp(16),
            color=(0, 0, 0, 1),  # 黑色文字
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(message_label)
        
        # 确定按钮
        ok_button = GradientButton(
            text='确定',
            font_size=dp(16),
            bold=True,
            bg_color=get_color('primary'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(ok_button)
        
        # 创建弹窗
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False,
            title_size=dp(18),
            title_align='center',
            separator_height=dp(2),
            separator_color=get_color('primary'),
            background=''
        )
        
        # 直接设置弹窗背景为白色
        popup.canvas.before.clear()
        with popup.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(pos=popup.pos, size=popup.size)
        
        # 绑定位置和大小变化
        def update_bg(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(1, 1, 1, 1)
                Rectangle(pos=instance.pos, size=instance.size)
        
        popup.bind(pos=update_bg)
        popup.bind(size=update_bg)
        
        # 绑定确定按钮事件
        ok_button.bind(on_press=popup.dismiss)
        
        popup.open()


class AdminMainScreen(Screen):
    """管理员主页面"""
    name = StringProperty('admin_main')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # 根布局
        root = FloatLayout()
        
        # 背景渐变
        with root.canvas.before:
            Color(0.94, 0.95, 0.98, 1)
            Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)
        
        # 主卡片 - 调整高度和间距，位置靠上
        card = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint=(0.92, None),
            height=dp(400),
            pos_hint={'center_x': 0.5, 'top': 0.95}
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(20)])
        card.bind(pos=self.update_card, size=self.update_card)
        
        # 标题区域
        title_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80))
        
        # 标题（居中显示）
        title_label = Label(
            text='管理员中心',
            font_size=dp(24),
            bold=True,
            color=get_color('text_primary'),
            halign='center',
            valign='middle'
        )
        title_box.add_widget(title_label)
        
        card.add_widget(title_box)
        
        # 功能按钮布局
        button_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        button_layout.bind(minimum_height=button_layout.setter('height'))
        
        # 发布菜品按钮
        dish_button = GradientButton(
            text='发布菜品',
            font_size=dp(17),
            bold=True,
            bg_color=get_color('primary'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(60)
        )
        dish_button.bind(on_press=self.go_to_dish_publish)
        button_layout.add_widget(dish_button)
        
        # 发布社区通知按钮
        notice_button = GradientButton(
            text='发布社区通知',
            font_size=dp(17),
            bold=True,
            bg_color=get_color('secondary'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(60)
        )
        notice_button.bind(on_press=self.go_to_notice_publish)
        button_layout.add_widget(notice_button)
        
        # 退出按钮
        logout_button = GradientButton(
            text='退出登录',
            font_size=dp(15),
            bg_color=get_color('danger'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        logout_button.bind(on_press=self.logout)
        button_layout.add_widget(logout_button)
        
        card.add_widget(button_layout)
        
        root.add_widget(card)
        self.add_widget(root)
    
    def update_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.98, 0.98, 1, 1)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def update_card(self, instance, value):
        self.card_rect.pos = instance.pos
        self.card_rect.size = instance.size
    
    def go_to_dish_publish(self, instance):
        """跳转到菜品发布页面"""
        self.manager.current = 'dish_publish'
    
    def go_to_notice_publish(self, instance):
        """跳转到通知发布页面"""
        self.manager.current = 'notice_publish'
    
    def logout(self, instance):
        """退出登录"""
        self.manager.current = 'admin_login'


class DishPublishScreen(Screen):
    """菜品发布页面"""
    name = StringProperty('dish_publish')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # 根布局
        root = FloatLayout()
        
        # 背景渐变
        with root.canvas.before:
            Color(0.94, 0.95, 0.98, 1)
            Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)
        
        # 主卡片 - 调整高度和间距
        card = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(12),
            size_hint=(0.92, 0.88),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(20)])
        card.bind(pos=self.update_card, size=self.update_card)
        
        # 标题区域
        title_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80))
        
        # 标题（居中显示）
        title_label = Label(
            text='发布菜品',
            font_size=dp(24),
            bold=True,
            color=get_color('text_primary'),
            halign='center',
            valign='middle'
        )
        title_box.add_widget(title_label)
        
        card.add_widget(title_box)
        
        # 表单区域
        form_box = BoxLayout(orientation='vertical', spacing=dp(12))
        
        # 菜品名称标签
        name_label = Label(
            text='菜品名称',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        name_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(name_label)
        
        # 菜品名称输入
        self.name_input = TextInput(
            hint_text='请输入菜品名称',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        form_box.add_widget(self.name_input)
        
        # 菜品价格标签
        price_label = Label(
            text='菜品价格',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        price_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(price_label)
        
        # 菜品价格输入
        self.price_input = TextInput(
            hint_text='请输入菜品价格',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        form_box.add_widget(self.price_input)
        
        # 菜品描述标签
        description_label = Label(
            text='菜品描述',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        description_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(description_label)
        
        # 菜品描述输入
        self.description_input = TextInput(
            hint_text='请输入菜品描述',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(100),
            multiline=True,
            foreground_color=get_color('text_primary'),
            background_color=get_color('card')
        )
        form_box.add_widget(self.description_input)
        
        # 菜品分类标签
        category_label = Label(
            text='菜品分类',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        category_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(category_label)
        
        # 菜品分类输入
        self.category_input = TextInput(
            hint_text='请输入菜品分类',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        form_box.add_widget(self.category_input)
        
        card.add_widget(form_box)
        
        # 按钮区域
        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        
        # 发布按钮
        publish_btn = GradientButton(
            text='发布',
            font_size=dp(16),
            bold=True,
            bg_color=get_color('success'),
            color=(1, 1, 1, 1),
            size_hint_x=0.5
        )
        publish_btn.bind(on_press=self.publish_dish)
        btn_box.add_widget(publish_btn)
        
        # 取消按钮
        cancel_btn = GradientButton(
            text='取消',
            font_size=dp(16),
            bg_color=get_color('danger'),
            color=(1, 1, 1, 1),
            size_hint_x=0.5
        )
        cancel_btn.bind(on_press=self.go_back)
        btn_box.add_widget(cancel_btn)
        
        card.add_widget(btn_box)
        
        root.add_widget(card)
        self.add_widget(root)
    
    def update_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.98, 0.98, 1, 1)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def update_card(self, instance, value):
        self.card_rect.pos = instance.pos
        self.card_rect.size = instance.size
    
    def publish_dish(self, instance):
        """发布菜品"""
        name = self.name_input.text.strip()
        price = self.price_input.text.strip()
        description = self.description_input.text.strip()
        category = self.category_input.text.strip()
        
        # 验证输入
        if not name:
            self.show_popup('错误', '请输入菜品名称')
            return
        
        if not price or not price.replace('.', '').isdigit():
            self.show_popup('错误', '请输入有效的价格')
            return
        
        # 发布菜品
        if self.create_dish(name, float(price), description, category):
            self.show_popup('成功', '菜品发布成功')
            # 清空表单
            self.name_input.text = ''
            self.price_input.text = ''
            self.description_input.text = ''
            self.category_input.text = ''
        else:
            self.show_popup('错误', '菜品发布失败')
    
    def create_dish(self, name, price, description, category):
        """创建菜品"""
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO dishes (name, price, description, category, is_available)
                VALUES (?, ?, ?, ?, ?)
                ''', (name, price, description, category, 1))
                conn.commit()
                close_db_connection(conn)
                return True
            return False
        except Exception as e:
            print(f"创建菜品失败: {e}")
            return False
    
    def go_back(self, instance):
        """返回管理员主页面"""
        self.manager.current = 'admin_main'
    
    def show_popup(self, title, message):
        """显示弹窗"""
        # 创建弹窗内容布局
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # 消息标签
        message_label = Label(
            text=message,
            font_size=dp(16),
            color=(0, 0, 0, 1),  # 黑色文字
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(message_label)
        
        # 确定按钮
        ok_button = GradientButton(
            text='确定',
            font_size=dp(16),
            bold=True,
            bg_color=get_color('primary'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(ok_button)
        
        # 创建弹窗
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False,
            title_size=dp(18),
            title_align='center',
            separator_height=dp(2),
            separator_color=get_color('primary'),
            background=''
        )
        
        # 直接设置弹窗背景为白色
        popup.canvas.before.clear()
        with popup.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(pos=popup.pos, size=popup.size)
        
        # 绑定位置和大小变化
        def update_bg(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(1, 1, 1, 1)
                Rectangle(pos=instance.pos, size=instance.size)
        
        popup.bind(pos=update_bg)
        popup.bind(size=update_bg)
        
        # 绑定确定按钮事件
        ok_button.bind(on_press=popup.dismiss)
        
        popup.open()


class NoticePublishScreen(Screen):
    """社区通知发布页面"""
    name = StringProperty('notice_publish')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        # 根布局
        root = FloatLayout()
        
        # 背景渐变
        with root.canvas.before:
            Color(0.94, 0.95, 0.98, 1)
            Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=self.update_bg, size=self.update_bg)
        
        # 主卡片 - 调整高度和间距
        card = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(12),
            size_hint=(0.92, 0.88),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.card_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(20)])
        card.bind(pos=self.update_card, size=self.update_card)
        
        # 标题区域
        title_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(80))
        
        # 标题（居中显示）
        title_label = Label(
            text='发布社区通知',
            font_size=dp(24),
            bold=True,
            color=get_color('text_primary'),
            halign='center',
            valign='middle'
        )
        title_box.add_widget(title_label)
        
        card.add_widget(title_box)
        
        # 表单区域
        form_box = BoxLayout(orientation='vertical', spacing=dp(12))
        
        # 通知标题标签
        title_label = Label(
            text='通知标题',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        title_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(title_label)
        
        # 通知标题输入
        self.title_input = TextInput(
            hint_text='请输入通知标题',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        form_box.add_widget(self.title_input)
        
        # 通知内容标签
        content_label = Label(
            text='通知内容',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        content_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(content_label)
        
        # 通知内容输入
        self.content_input = TextInput(
            hint_text='请输入通知内容',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(200),
            multiline=True,
            foreground_color=get_color('text_primary'),
            background_color=get_color('card')
        )
        form_box.add_widget(self.content_input)
        
        # 发布人标签
        author_label = Label(
            text='发布人',
            font_size=dp(13),
            color=get_color('text_secondary'),
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        author_label.bind(size=lambda s, v: setattr(s, 'text_size', (s.width, None)))
        form_box.add_widget(author_label)
        
        # 发布人输入
        self.author_input = TextInput(
            hint_text='请输入发布人',
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            foreground_color=get_color('text_primary'),
            background_color=get_color('card'),
            multiline=False
        )
        form_box.add_widget(self.author_input)
        
        card.add_widget(form_box)
        
        # 按钮区域
        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
        
        # 发布按钮
        publish_btn = GradientButton(
            text='发布',
            font_size=dp(16),
            bold=True,
            bg_color=get_color('success'),
            color=(1, 1, 1, 1),
            size_hint_x=0.5
        )
        publish_btn.bind(on_press=self.publish_notice)
        btn_box.add_widget(publish_btn)
        
        # 取消按钮
        cancel_btn = GradientButton(
            text='取消',
            font_size=dp(16),
            bg_color=get_color('danger'),
            color=(1, 1, 1, 1),
            size_hint_x=0.5
        )
        cancel_btn.bind(on_press=self.go_back)
        btn_box.add_widget(cancel_btn)
        
        card.add_widget(btn_box)
        
        root.add_widget(card)
        self.add_widget(root)
    
    def update_bg(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.98, 0.98, 1, 1)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def update_card(self, instance, value):
        self.card_rect.pos = instance.pos
        self.card_rect.size = instance.size
    
    def publish_notice(self, instance):
        """发布社区通知"""
        title = self.title_input.text.strip()
        content = self.content_input.text.strip()
        author = self.author_input.text.strip()
        
        # 验证输入
        if not title:
            self.show_popup('错误', '请输入通知标题')
            return
        
        if not content:
            self.show_popup('错误', '请输入通知内容')
            return
        
        # 发布通知
        if self.create_notice(title, content, author):
            self.show_popup('成功', '通知发布成功')
            # 清空表单
            self.title_input.text = ''
            self.content_input.text = ''
            self.author_input.text = ''
        else:
            self.show_popup('错误', '通知发布失败')
    
    def create_notice(self, title, content, author):
        """创建社区通知"""
        try:
            print(f"开始创建通知: title={title}, content={content}, author={author}")
            conn = get_db_connection()
            print(f"数据库连接: {conn}")
            if conn:
                cursor = conn.cursor()
                print("获取游标成功")
                # 检查表是否存在
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notices'")
                table_exists = cursor.fetchone()
                print(f"表 notices 存在: {table_exists}")
                
                # 插入数据
                cursor.execute('''
                INSERT INTO notices (title, content, author, is_active)
                VALUES (?, ?, ?, ?)
                ''', (title, content, author, 1))
                print("插入数据成功")
                conn.commit()
                print("提交事务成功")
                close_db_connection(conn)
                print("关闭连接成功")
                return True
            else:
                print("获取数据库连接失败")
                return False
        except Exception as e:
            print(f"创建通知失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def go_back(self, instance):
        """返回管理员主页面"""
        self.manager.current = 'admin_main'
    
    def show_popup(self, title, message):
        """显示弹窗"""
        # 创建弹窗内容布局
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # 消息标签
        message_label = Label(
            text=message,
            font_size=dp(16),
            color=(0, 0, 0, 1),  # 黑色文字
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(message_label)
        
        # 确定按钮
        ok_button = GradientButton(
            text='确定',
            font_size=dp(16),
            bold=True,
            bg_color=get_color('primary'),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(ok_button)
        
        # 创建弹窗
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4),
            auto_dismiss=False,
            title_size=dp(18),
            title_align='center',
            separator_height=dp(2),
            separator_color=get_color('primary'),
            background=''
        )
        
        # 直接设置弹窗背景为白色
        popup.canvas.before.clear()
        with popup.canvas.before:
            Color(1, 1, 1, 1)
            Rectangle(pos=popup.pos, size=popup.size)
        
        # 绑定位置和大小变化
        def update_bg(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(1, 1, 1, 1)
                Rectangle(pos=instance.pos, size=instance.size)
        
        popup.bind(pos=update_bg)
        popup.bind(size=update_bg)
        
        # 绑定确定按钮事件
        ok_button.bind(on_press=popup.dismiss)
        
        popup.open()
