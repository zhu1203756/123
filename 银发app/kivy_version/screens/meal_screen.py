"""
订餐服务页面 - 使用统一UI样式
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from screens.base_screen import BaseScreen
from styles import get_color, get_font_size, get_button_color, DIMENSIONS
from database import get_db_connection, close_db_connection


class MealScreen(BaseScreen):
    name = StringProperty('meal')
    
    def __init__(self, voice_engine, meal_service, db_manager, app, **kwargs):
        self.title = '订餐服务'
        super().__init__(voice_engine, app, **kwargs)
        self.meal_service = meal_service
        self.db_manager = db_manager
        self.selected_items = []
        
        self.build_ui()
        self.load_saved_order_info()
        self.load_menu_items()
    
    def load_menu_items(self):
        """从数据库加载菜单项"""
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, price, description FROM dishes WHERE is_available = 1')
                menu_items = []
                for row in cursor.fetchall():
                    menu_items.append({
                        'id': row[0],
                        'name': row[1],
                        'price': f'{row[2]}元',
                        'desc': row[3] or ''
                    })
                close_db_connection(conn)
                
                # 清空当前菜单列表
                for child in self.menu_list.children:
                    self.menu_list.remove_widget(child)
                
                # 添加从数据库加载的菜单项
                for item in menu_items:
                    item_row = self._create_menu_item(item)
                    self.menu_list.add_widget(item_row)
        except Exception as e:
            print(f"加载菜品失败: {e}")
    
    def build_ui(self):
        """构建订餐界面"""
        # 调用基础类构建框架
        super().build_ui()
        
        # 内容区域
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        # 配送信息卡片
        info_card = self.create_card(orientation='vertical', size_hint=(1, 0.35), 
                                     padding=15, spacing=10)
        
        # 卡片标题
        info_title = Label(
            text='配送信息',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=35,
            halign='left'
        )
        info_title.bind(size=info_title.setter('text_size'))
        info_card.add_widget(info_title)
        
        # 地址选择
        addr_label = Label(
            text='配送地址',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=25,
            halign='left'
        )
        addr_label.bind(size=addr_label.setter('text_size'))
        info_card.add_widget(addr_label)
        
        # 地址下拉菜单
        self.address_spinner, spinner_layout = self.create_spinner(
            text='选择地址',
            values=['选择地址'],
            size_hint=(1, None),
            height=45
        )
        self.address_spinner.bind(text=self.on_address_change)
        info_card.add_widget(spinner_layout)
        
        # 手动输入地址
        self.address_input = TextInput(
            hint_text='手动输入详细配送地址',
            font_size=get_font_size('body'),
            size_hint=(1, None),
            height=45,
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[10, 10]
        )
        info_card.add_widget(self.address_input)
        
        # 电话输入
        phone_label = Label(
            text='联系电话',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=25,
            halign='left'
        )
        phone_label.bind(size=phone_label.setter('text_size'))
        info_card.add_widget(phone_label)
        
        phone_layout = BoxLayout(size_hint=(1, None), height=45, spacing=10)
        
        self.phone_spinner, spinner_layout = self.create_spinner(
            text='选择联系人',
            values=['选择联系人', '本人', '子女', '其他'],
            size_hint=(0.4, 1)
        )
        phone_layout.add_widget(spinner_layout)
        
        self.phone_input = TextInput(
            hint_text='输入电话号码',
            font_size=get_font_size('body'),
            size_hint=(0.6, 1),
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[10, 10]
        )
        phone_layout.add_widget(self.phone_input)
        
        info_card.add_widget(phone_layout)
        content.add_widget(info_card)
        
        # 菜单卡片
        menu_card = self.create_card(orientation='vertical', size_hint=(1, 0.5), 
                                     padding=15, spacing=10)
        # 确保菜单卡片内部有正确的背景色
        menu_card.canvas.before.clear()
        with menu_card.canvas.before:
            Color(*get_color('card'))
            RoundedRectangle(size=menu_card.size, pos=menu_card.pos,
                           radius=[DIMENSIONS['card_radius']])
        
        def update_menu_card_bg(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*get_color('card'))
                RoundedRectangle(size=instance.size, pos=instance.pos,
                               radius=[DIMENSIONS['card_radius']])
        
        menu_card.bind(size=update_menu_card_bg, pos=update_menu_card_bg)
        
        menu_title = Label(
            text='今日菜单',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=35,
            halign='left'
        )
        menu_title.bind(size=menu_title.setter('text_size'))
        menu_card.add_widget(menu_title)
        
        # 菜单列表
        menu_scroll = ScrollView(size_hint=(1, 1))
        # 创建一个容器，用于设置背景色
        menu_container = BoxLayout(orientation='vertical', size_hint=(1, 1), padding=5)
        # 设置容器背景色
        with menu_container.canvas.before:
            Color(*get_color('card'))
            Rectangle(size=menu_container.size, pos=menu_container.pos)
        
        def update_container_bg(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*get_color('card'))
                Rectangle(size=instance.size, pos=instance.pos)
        
        menu_container.bind(size=update_container_bg, pos=update_container_bg)
        
        # 菜单列表
        self.menu_list = BoxLayout(orientation='vertical', size_hint=(1, None), 
                              spacing=8, padding=0)
        self.menu_list.bind(minimum_height=self.menu_list.setter('height'))
        
        # 将菜单列表添加到容器中
        menu_container.add_widget(self.menu_list)
        
        # 初始空列表（将由 load_menu_items 方法填充）
        menu_scroll.add_widget(menu_container)
        menu_card.add_widget(menu_scroll)
        content.add_widget(menu_card)
        
        # 底部操作栏
        action_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.12), 
                               spacing=15, padding=[0, 5])
        
        # 总价显示
        self.total_label = Label(
            text='合计：0元',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(0.4, 1)
        )
        action_bar.add_widget(self.total_label)
        
        # 提交订单按钮
        submit_btn = self.create_button(
            text='提交订单',
            color_key='primary',
            size_hint=(0.6, 1),
            on_press=self.submit_order
        )
        action_bar.add_widget(submit_btn)
        
        content.add_widget(action_bar)
        
        self.content_area.add_widget(content)
    
    def _create_menu_item(self, item):
        """创建菜单项"""
        row = BoxLayout(orientation='horizontal', size_hint=(1, None), 
                       height=70, spacing=10, padding=5)
        
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
        
        # 选择框
        checkbox = CheckBox(size_hint=(0.1, 1))
        checkbox.bind(active=lambda cb, val, name=item['name']: 
                     self.on_item_select(name, val))
        row.add_widget(checkbox)
        
        # 菜品信息
        info_layout = BoxLayout(orientation='vertical', size_hint=(0.6, 1), 
                               padding=[5, 5])
        name_label = Label(
            text=item['name'],
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('text_primary'),
            size_hint=(1, 0.6),
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        desc_label = Label(
            text=item['desc'],
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, 0.4),
            halign='left'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(desc_label)
        row.add_widget(info_layout)
        
        # 价格
        price_label = Label(
            text=item['price'],
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('success'),
            size_hint=(0.3, 1)
        )
        row.add_widget(price_label)
        
        return row
    
    def on_item_select(self, item_name, is_selected):
        """处理菜品选择"""
        if is_selected:
            self.selected_items.append(item_name)
            self.voice_engine.speak(f"已选择{item_name}")
        else:
            self.selected_items.remove(item_name)
        
        # 更新总价
        total = len(self.selected_items) * 25  # 简化计算
        self.total_label.text = f'合计：{total}元'
    
    def submit_order(self):
        """提交订单"""
        if not self.selected_items:
            self.voice_engine.speak("请先选择菜品")
            return
        
        if not self.address_input.text.strip():
            self.voice_engine.speak("请输入配送地址")
            return
        
        self.voice_engine.speak("订单提交成功")
        # 保存订单信息
        self.save_order_info()
        # 显示订单提交成功窗口
        self.show_order_success()
    
    def show_order_success(self):
        """显示订单提交成功窗口"""
        # 创建弹窗内容
        content = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        content.height = 200
        
        # 标题
        title = Label(
            text='订单提交成功',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            halign='center',
            size_hint=(1, None),
            height=50
        )
        content.add_widget(title)
        
        # 订单信息
        info = Label(
            text=f"配送地址: {self.address_input.text}\n联系电话: {self.phone_input.text}",
            font_size=get_font_size('body'),
            color=get_color('text_primary'),
            halign='center',
            text_size=(300, None),
            size_hint=(1, None),
            height=80
        )
        content.add_widget(info)
        
        # 确认按钮
        from kivy.uix.button import Button
        ok_button = Button(
            text='确定',
            font_size=get_font_size('body'),
            size_hint=(0.5, None),
            height=45,
            background_color=get_color('primary'),
            color=(1, 1, 1, 1)
        )
        
        # 创建弹窗
        popup = Popup(
            title='',
            content=content,
            size_hint=(0.7, 0.5),
            auto_dismiss=False,
            background='',  # 透明背景
            separator_height=0
        )
        
        # 设置弹窗内容背景为白色
        with content.canvas.before:
            Color(1, 1, 1, 1)  # 白色背景
            Rectangle(size=content.size, pos=content.pos)
        
        # 绑定按钮事件
        def on_ok(instance):
            print("点击了确定按钮")
            popup.dismiss()
            print("弹窗已关闭")
        
        ok_button.bind(on_press=on_ok)
        
        # 按钮布局
        button_layout = BoxLayout(size_hint=(1, None), height=50, padding=[100, 0])
        button_layout.add_widget(ok_button)
        content.add_widget(button_layout)
        
        # 显示弹窗
        popup.open()
        print("弹窗已打开")
    
    def save_order_info(self):
        """保存订单信息到数据库"""
        try:
            address = self.address_input.text.strip()
            phone = self.phone_input.text.strip()
            contact = self.phone_spinner.text
            
            if not address or not phone:
                return
            
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                # 检查是否已存在相同地址
                cursor.execute('SELECT id FROM user_addresses WHERE address = ? AND phone = ?', 
                              (address, phone))
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有地址
                    cursor.execute('''
                    UPDATE user_addresses 
                    SET contact_name = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                    ''', (contact, existing[0]))
                else:
                    # 插入新地址
                    cursor.execute('''
                    INSERT INTO user_addresses (address, phone, contact_name, is_default)
                    VALUES (?, ?, ?, ?)
                    ''', (address, phone, contact, 1))
                
                conn.commit()
                close_db_connection(conn)
                print(f"地址保存成功: {address}")
        except Exception as e:
            print(f"保存地址失败: {e}")
    
    def on_address_change(self, spinner, text):
        """处理地址选择变化"""
        if text != '选择地址':
            # 从地址中提取地址和电话
            try:
                # 地址格式: 地址 (电话)
                if ' (' in text and ')' in text:
                    addr_part, phone_part = text.rsplit(' (', 1)
                    phone = phone_part.rstrip(')')
                    self.address_input.text = addr_part
                    self.phone_input.text = phone
            except Exception as e:
                print(f"解析地址失败: {e}")
    
    def load_saved_order_info(self):
        """加载保存的订单信息"""
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                # 加载所有地址
                cursor.execute('''
                SELECT address, phone, contact_name FROM user_addresses 
                ORDER BY updated_at DESC
                ''')
                addresses = cursor.fetchall()
                
                # 填充地址下拉菜单
                address_values = ['选择地址']
                default_address = None
                
                for addr in addresses:
                    address_str = f"{addr[0]} ({addr[1]})"
                    address_values.append(address_str)
                    if not default_address:
                        default_address = addr
                
                self.address_spinner.values = address_values
                
                # 加载默认地址
                if default_address:
                    self.address_input.text = default_address[0]
                    self.phone_input.text = default_address[1]
                    if default_address[2] in ['本人', '子女', '其他']:
                        self.phone_spinner.text = default_address[2]
                    print(f"地址加载成功: {default_address[0]}")
                
                close_db_connection(conn)
        except Exception as e:
            print(f"加载地址失败: {e}")
