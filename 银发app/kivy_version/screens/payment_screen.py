"""
缴费服务页面 - 使用统一UI样式
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.graphics import Color, RoundedRectangle
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from screens.base_screen import BaseScreen
from styles import get_color, get_font_size, DIMENSIONS


class PaymentScreen(BaseScreen):
    name = StringProperty('payment')
    
    def __init__(self, voice_engine, payment_service, db_manager, app, **kwargs):
        self.title = '缴费服务'
        super().__init__(voice_engine, app, **kwargs)
        self.payment_service = payment_service
        self.db_manager = db_manager
        
        self.build_ui()
    
    def build_ui(self):
        """构建缴费界面"""
        super().build_ui()
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        # 缴费类型卡片
        type_card = self.create_card(orientation='vertical', size_hint=(1, 0.25),
                                     padding=15, spacing=10)
        
        type_title = Label(
            text='选择缴费类型',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=35,
            halign='left'
        )
        type_title.bind(size=type_title.setter('text_size'))
        type_card.add_widget(type_title)
        
        self.payment_type_spinner, spinner_layout = self.create_spinner(
            text='选择缴费类型',
            values=('水费', '电费', '燃气费', '电话费', '物业费', '宽带费'),
            size_hint=(1, None),
            height=50
        )
        type_card.add_widget(spinner_layout)
        
        content.add_widget(type_card)
        
        # 账户信息卡片
        account_card = self.create_card(orientation='vertical', size_hint=(1, 0.35),
                                        padding=15, spacing=10)
        
        account_title = Label(
            text='账户信息',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=35,
            halign='left'
        )
        account_title.bind(size=account_title.setter('text_size'))
        account_card.add_widget(account_title)
        
        # 户号输入
        account_label = Label(
            text='缴费户号',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=25,
            halign='left'
        )
        account_label.bind(size=account_label.setter('text_size'))
        account_card.add_widget(account_label)
        
        self.account_input = TextInput(
            hint_text='请输入缴费户号',
            font_size=get_font_size('body'),
            size_hint=(1, None),
            height=45,
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[10, 10]
        )
        account_card.add_widget(self.account_input)
        
        # 户名输入
        name_label = Label(
            text='户名（选填）',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=25,
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))
        account_card.add_widget(name_label)
        
        self.name_input = TextInput(
            hint_text='请输入户名',
            font_size=get_font_size('body'),
            size_hint=(1, None),
            height=45,
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[10, 10]
        )
        account_card.add_widget(self.name_input)
        
        content.add_widget(account_card)
        
        # 待缴费账单卡片
        bill_card = self.create_card(orientation='vertical', size_hint=(1, 0.28),
                                     padding=15, spacing=10)
        
        bill_title = Label(
            text='待缴费账单',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=35,
            halign='left'
        )
        bill_title.bind(size=bill_title.setter('text_size'))
        bill_card.add_widget(bill_title)
        
        # 账单列表
        bill_scroll = ScrollView(size_hint=(1, 1))
        bill_list = BoxLayout(orientation='vertical', size_hint=(1, None),
                              spacing=8, padding=5)
        bill_list.bind(minimum_height=bill_list.setter('height'))
        
        # 示例账单
        bills = [
            {'type': '水费', 'amount': '45.50', 'date': '2024-03'},
            {'type': '电费', 'amount': '128.00', 'date': '2024-03'},
        ]
        
        for bill in bills:
            bill_row = self._create_bill_item(bill)
            bill_list.add_widget(bill_row)
        
        bill_scroll.add_widget(bill_list)
        bill_card.add_widget(bill_scroll)
        
        content.add_widget(bill_card)
        
        # 底部操作栏
        action_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.12),
                               spacing=15, padding=[0, 5])
        
        # 查询按钮
        query_btn = self.create_button(
            text='查询账单',
            color_key='secondary',
            size_hint=(0.5, 1),
            on_press=self.query_bill
        )
        action_bar.add_widget(query_btn)
        
        # 缴费按钮
        pay_btn = self.create_button(
            text='立即缴费',
            color_key='success',
            size_hint=(0.5, 1),
            on_press=self.make_payment
        )
        action_bar.add_widget(pay_btn)
        
        content.add_widget(action_bar)
        
        self.content_area.add_widget(content)
    
    def _create_bill_item(self, bill):
        """创建账单项"""
        row = BoxLayout(orientation='horizontal', size_hint=(1, None),
                       height=60, spacing=10, padding=5)
        
        with row.canvas.before:
            Color(*get_color('background'))
            RoundedRectangle(size=row.size, pos=row.pos,
                           radius=[DIMENSIONS['card_radius']])
        
        def update_row(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*get_color('background'))
                RoundedRectangle(size=instance.size, pos=instance.pos,
                               radius=[DIMENSIONS['card_radius']])
        
        row.bind(size=update_row, pos=update_row)
        
        # 类型
        type_label = Label(
            text=bill['type'],
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('text_primary'),
            size_hint=(0.3, 1)
        )
        row.add_widget(type_label)
        
        # 日期
        date_label = Label(
            text=bill['date'],
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(0.3, 1)
        )
        row.add_widget(date_label)
        
        # 金额
        amount_label = Label(
            text=f"¥{bill['amount']}",
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('danger'),
            size_hint=(0.4, 1)
        )
        row.add_widget(amount_label)
        
        return row
    
    def query_bill(self):
        """查询账单"""
        bill_type = self.payment_type_spinner.text
        if bill_type == '选择缴费类型':
            self.voice_engine.speak("请先选择缴费类型")
            return
        
        account = self.account_input.text.strip()
        if not account:
            self.voice_engine.speak("请输入缴费户号")
            return
        
        self.voice_engine.speak(f"正在查询{bill_type}账单")
        # 调用查询服务
    
    def make_payment(self):
        """缴费"""
        self.voice_engine.speak("正在处理缴费")
        # 调用缴费服务
