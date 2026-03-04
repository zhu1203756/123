"""
紧急呼叫页面 - 使用统一UI样式
支持一键呼叫、定位、发送短信等功能
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock
import sys
import os
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from screens.base_screen import BaseScreen
from styles import get_color, get_font_size, DIMENSIONS


class EmergencyScreen(BaseScreen):
    name = StringProperty('emergency')
    
    def __init__(self, voice_engine, community_service, db_manager, app, **kwargs):
        self.title = '紧急呼叫'
        super().__init__(voice_engine, app, **kwargs)
        self.community_service = community_service
        self.db_manager = db_manager
        self.current_location = None
        
        self.build_ui()
        Clock.schedule_once(lambda dt: self.load_contacts(), 0.5)
        Clock.schedule_once(lambda dt: self.update_location(), 1.0)
    
    def build_ui(self):
        """构建紧急呼叫界面"""
        super().build_ui()
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        # 位置信息卡片
        location_card = self.create_card(orientation='horizontal', size_hint=(1, None),
                                         height=60, padding=10, spacing=10)
        
        location_icon = Label(
            text='位置',
            font_size=14,
            size_hint=(0.1, 1)
        )
        location_card.add_widget(location_icon)
        
        self.location_label = Label(
            text='正在获取位置...',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(0.7, 1),
            halign='left'
        )
        self.location_label.bind(size=self.location_label.setter('text_size'))
        location_card.add_widget(self.location_label)
        
        refresh_btn = self.create_button(
            text='刷新',
            color_key='secondary',
            size_hint=(0.2, 1),
            on_press=self.update_location
        )
        location_card.add_widget(refresh_btn)
        
        content.add_widget(location_card)
        
        # 紧急呼叫按钮卡片
        emergency_card = self.create_card(orientation='vertical', size_hint=(1, 0.3),
                                          padding=20, spacing=15)
        
        # 大红色紧急按钮
        emergency_btn = BoxLayout(orientation='vertical', size_hint=(1, 1))
        
        with emergency_btn.canvas.before:
            Color(*get_color('danger'))
            RoundedRectangle(size=emergency_btn.size, pos=emergency_btn.pos,
                           radius=[20])
        
        def update_btn(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*get_color('danger'))
                RoundedRectangle(size=instance.size, pos=instance.pos,
                               radius=[20])
        
        emergency_btn.bind(size=update_btn, pos=update_btn)
        
        # 图标已删除
        
        # 文字
        text_label = Label(
            text='一键紧急呼叫',
            font_size=get_font_size('title'),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.3)
        )
        emergency_btn.add_widget(text_label)
        
        # 提示
        hint_label = Label(
            text='点击立即联系紧急联系人',
            font_size=get_font_size('caption'),
            color=(1, 1, 1, 0.8),
            size_hint=(1, 0.2)
        )
        emergency_btn.add_widget(hint_label)
        
        emergency_btn.bind(on_touch_down=self.on_emergency_touch)
        
        emergency_card.add_widget(emergency_btn)
        content.add_widget(emergency_card)
        
        # 快捷呼叫按钮
        quick_call_card = self.create_card(orientation='vertical', size_hint=(1, None),
                                           height=120, padding=15, spacing=10)
        
        quick_title = Label(
            text='快捷呼叫',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=30,
            halign='left'
        )
        quick_title.bind(size=quick_title.setter('text_size'))
        quick_call_card.add_widget(quick_title)
        
        quick_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1),
                                 spacing=10)
        
        # 120急救
        call_120_btn = self.create_button(
            text='120\n急救电话',
            color_key='danger',
            size_hint=(0.33, 1),
            on_press=lambda x: self.call_number('120', '急救中心')
        )
        quick_layout.add_widget(call_120_btn)
        
        # 110报警
        call_110_btn = self.create_button(
            text='110\n报警电话',
            color_key='primary',
            size_hint=(0.33, 1),
            on_press=lambda x: self.call_number('110', '报警中心')
        )
        quick_layout.add_widget(call_110_btn)
        
        # 119火警
        call_119_btn = self.create_button(
            text='119\n火警电话',
            color_key='warning',
            size_hint=(0.33, 1),
            on_press=lambda x: self.call_number('119', '消防中心')
        )
        quick_layout.add_widget(call_119_btn)
        
        quick_call_card.add_widget(quick_layout)
        content.add_widget(quick_call_card)
        
        # 紧急联系人卡片
        contacts_card = self.create_card(orientation='vertical', size_hint=(1, 0.35),
                                         padding=15, spacing=10)
        
        contacts_header = BoxLayout(orientation='horizontal', size_hint=(1, None),
                                    height=35)
        
        contacts_title = Label(
            text='紧急联系人',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(0.6, 1),
            halign='left'
        )
        contacts_title.bind(size=contacts_title.setter('text_size'))
        contacts_header.add_widget(contacts_title)
        
        add_btn = self.create_button(
            text='+ 添加',
            color_key='success',
            size_hint=(0.4, 1),
            on_press=self.add_contact
        )
        contacts_header.add_widget(add_btn)
        
        contacts_card.add_widget(contacts_header)
        
        # 联系人列表
        contacts_scroll = ScrollView(size_hint=(1, 1))
        self.contacts_list = BoxLayout(orientation='vertical', size_hint=(1, None),
                                       spacing=10, padding=5)
        self.contacts_list.bind(minimum_height=self.contacts_list.setter('height'))
        
        contacts_scroll.add_widget(self.contacts_list)
        contacts_card.add_widget(contacts_scroll)
        
        content.add_widget(contacts_card)
        
        # 提示信息
        tip_card = self.create_card(orientation='vertical', size_hint=(1, None),
                                    height=100, padding=15)
        
        tip_label = Label(
            text='紧急情况下，系统会自动获取您的位置，\n并发送包含位置信息的求助短信给所有紧急联系人。',
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, 1)
        )
        tip_card.add_widget(tip_label)
        content.add_widget(tip_card)
        
        self.content_area.add_widget(content)
    
    def update_location(self, instance=None):
        """更新位置信息"""
        self.location_label.text = '正在获取位置...'
        
        # 尝试使用多种方式获取位置
        methods = [
            self._get_location_by_qq_map_ip,
            self._get_location_by_ipapi_co,
            self._get_location_by_ipinfo_io,
            self._get_location_by_backup
        ]
        
        for method in methods:
            try:
                location = method()
                if location:
                    # 更新位置信息
                    self.current_location = location
                    
                    # 更新UI
                    display_address = location['address'][:30] + '...' if len(location['address']) > 30 else location['address']
                    self.location_label.text = f'📍 {display_address}'
                    self.location_label.color = get_color('success')
                    
                    print(f"位置获取成功: {location['address']}")
                    return  # 成功获取位置，退出方法
            except Exception as e:
                print(f"使用{method.__name__}获取位置失败: {e}")
        
        # 所有方法都失败，使用默认位置
        print("所有位置获取方法都失败，使用默认位置")
        self.current_location = {
            'latitude': 39.9042,
            'longitude': 116.4074,
            'address': '北京市朝阳区'
        }
        self.location_label.text = '📍 北京市朝阳区'
        self.location_label.color = get_color('success')
    
    def _get_location_by_qq_map_ip(self):
        """使用腾讯地图IP定位获取位置"""
        # 1. 直接使用腾讯地图的定位服务，不需要单独获取IP
        api_key = 'BJMBZ-N5ALJ-LFYF2-XIPXN-AGPCQ-NEB36'
        
        # 2. 使用腾讯地图API进行IP定位（不指定IP，自动使用客户端IP）
        ip_location_url = f'https://apis.map.qq.com/ws/location/v1/ip?key={api_key}'
        print(f"调用腾讯地图API: {ip_location_url}")
        
        ip_location_response = requests.get(ip_location_url, timeout=10)
        ip_location_data = ip_location_response.json()
        
        print(f"IP定位响应: {ip_location_data}")
        
        if ip_location_data.get('status') != 0:
            raise Exception(f'IP定位失败: {ip_location_data.get("message", "未知错误")}')
        
        # 3. 获取经纬度
        location_data = ip_location_data.get('result', {}).get('location', {})
        latitude = location_data.get('lat')
        longitude = location_data.get('lng')
        
        if not latitude or not longitude:
            raise Exception('无法获取经纬度')
        
        print(f"获取到经纬度: {latitude}, {longitude}")
        
        # 4. 使用逆地址解析获取详细地址
        return self._get_address_by_coords(latitude, longitude, api_key)
    
    def _get_location_by_qq_map_geo(self):
        """使用腾讯地图地理编码获取位置（备用方法）"""
        # 直接使用北京作为默认城市进行地理编码
        api_key = 'BJMBZ-N5ALJ-LFYF2-XIPXN-AGPCQ-NEB36'
        city = '北京市'
        geo_url = f'https://apis.map.qq.com/ws/geocoder/v1/?address={city}&key={api_key}'
        
        geo_response = requests.get(geo_url, timeout=5)
        geo_data = geo_response.json()
        
        print(f"地理编码响应: {geo_data}")
        
        if geo_data.get('status') != 0:
            raise Exception(f'地理编码失败: {geo_data.get("message", "未知错误")}')
        
        # 获取经纬度
        location_data = geo_data.get('result', {}).get('location', {})
        latitude = location_data.get('lat')
        longitude = location_data.get('lng')
        
        if not latitude or not longitude:
            raise Exception('无法获取经纬度')
        
        print(f"获取到经纬度: {latitude}, {longitude}")
        
        # 使用逆地址解析获取详细地址
        return self._get_address_by_coords(latitude, longitude, api_key)
    
    def _get_address_by_coords(self, latitude, longitude, api_key):
        """根据经纬度获取详细地址"""
        reverse_geocode_url = f'https://apis.map.qq.com/ws/geocoder/v1/?location={latitude},{longitude}&key={api_key}'
        reverse_geocode_response = requests.get(reverse_geocode_url, timeout=5)
        reverse_geocode_data = reverse_geocode_response.json()
        
        print(f"逆地址解析响应: {reverse_geocode_data}")
        
        if reverse_geocode_data.get('status') != 0:
            raise Exception(f'逆地址解析失败: {reverse_geocode_data.get("message", "未知错误")}')
        
        # 获取详细地址信息
        address_data = reverse_geocode_data.get('result', {}).get('address_component', {})
        formatted_address = reverse_geocode_data.get('result', {}).get('formatted_address', '未知位置')
        
        # 构建详细地址
        province = address_data.get('province', '')
        city = address_data.get('city', '')
        district = address_data.get('district', '')
        street = address_data.get('street', '')
        street_number = address_data.get('street_number', '')
        
        # 优化地址格式
        address_parts = []
        if province:
            address_parts.append(province)
        if city and city != province:
            address_parts.append(city)
        if district:
            address_parts.append(district)
        if street:
            address_parts.append(street)
        if street_number:
            address_parts.append(street_number)
        
        full_address = ''.join(address_parts)
        if not full_address or full_address == '':
            full_address = formatted_address
        
        return {
            'latitude': latitude,
            'longitude': longitude,
            'address': full_address
        }
    
    def _get_location_by_ipapi_co(self):
        """使用ipapi.co获取位置"""
        # 使用ipapi.co获取IP地址和位置信息
        response = requests.get('https://ipapi.co/json/', timeout=5)
        data = response.json()
        
        print(f"ipapi.co响应: {data}")
        
        # 检查是否获取成功
        if 'error' in data:
            raise Exception(f'ipapi.co获取失败: {data.get("reason", "未知错误")}')
        
        # 提取位置信息
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        city = data.get('city', '')
        region = data.get('region', '')
        country = data.get('country_name', '')
        
        if not latitude or not longitude:
            raise Exception('无法获取经纬度')
        
        print(f"获取到经纬度: {latitude}, {longitude}")
        
        # 构建地址
        address_parts = []
        if country:
            address_parts.append(country)
        if region:
            address_parts.append(region)
        if city:
            address_parts.append(city)
        
        address = ''.join(address_parts)
        if not address:
            address = '未知位置'
        
        return {
            'latitude': latitude,
            'longitude': longitude,
            'address': address
        }
    
    def _get_location_by_ipinfo_io(self):
        """使用ipinfo.io获取位置"""
        # 使用ipinfo.io获取IP地址和位置信息
        response = requests.get('https://ipinfo.io/json', timeout=5)
        data = response.json()
        
        print(f"ipinfo.io响应: {data}")
        
        # 提取位置信息
        loc = data.get('loc')
        if not loc:
            raise Exception('无法获取经纬度')
        
        # 解析经纬度
        latitude, longitude = loc.split(',')
        city = data.get('city', '')
        region = data.get('region', '')
        country = data.get('country', '')
        
        print(f"获取到经纬度: {latitude}, {longitude}")
        
        # 国家代码到中文名称的映射
        country_map = {
            'CN': '中国',
            'US': '美国',
            'JP': '日本',
            'KR': '韩国',
            'GB': '英国',
            'FR': '法国',
            'DE': '德国',
            'CA': '加拿大',
            'AU': '澳大利亚',
            'NZ': '新西兰'
        }
        
        # 将国家代码转换为中文名称
        country_name = country_map.get(country, country)
        
        # 构建地址
        address_parts = []
        if country_name:
            address_parts.append(country_name)
        if region:
            address_parts.append(region)
        if city:
            address_parts.append(city)
        
        address = ''.join(address_parts)
        if not address:
            address = '未知位置'
        
        return {
            'latitude': float(latitude),
            'longitude': float(longitude),
            'address': address
        }
    
    def _get_location_by_backup(self):
        """使用备用方法获取位置"""
        # 返回一个默认位置
        return {
            'latitude': 39.9042,
            'longitude': 116.4074,
            'address': '北京市朝阳区'
        }
    
    def _create_contact_item(self, contact):
        """创建联系人项"""
        row = BoxLayout(orientation='horizontal', size_hint=(1, None),
                       height=70, spacing=10, padding=10)
        
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
        
        # 头像
        avatar = Label(
            text='',
            font_size=30,
            size_hint=(0.12, 1)
        )
        row.add_widget(avatar)
        
        # 信息
        info_layout = BoxLayout(orientation='vertical', size_hint=(0.4, 1))
        
        name_label = Label(
            text=contact.get('name', ''),
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('text_primary'),
            size_hint=(1, 0.6),
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        relation_label = Label(
            text=contact.get('relation', ''),
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, 0.4),
            halign='left'
        )
        relation_label.bind(size=relation_label.setter('text_size'))
        
        info_layout.add_widget(name_label)
        info_layout.add_widget(relation_label)
        row.add_widget(info_layout)
        
        # 电话
        phone_label = Label(
            text=contact.get('phone', ''),
            font_size=get_font_size('body'),
            color=get_color('primary'),
            size_hint=(0.28, 1)
        )
        row.add_widget(phone_label)
        
        # 呼叫按钮
        call_btn = self.create_button(
            text='呼叫',
            color_key='success',
            size_hint=(0.1, 1),
            on_press=lambda x, c=contact: self.call_contact(c)
        )
        row.add_widget(call_btn)
        
        # 删除按钮
        delete_btn = self.create_button(
            text='删除',
            color_key='danger',
            size_hint=(0.1, 1),
            on_press=lambda x, c=contact: self.delete_contact(c)
        )
        row.add_widget(delete_btn)
        
        return row
    
    def on_emergency_touch(self, instance, touch):
        """紧急按钮触摸事件"""
        if instance.collide_point(*touch.pos):
            self.trigger_emergency()
    
    def trigger_emergency(self):
        """触发紧急呼叫"""
        if self.voice_engine:
            self.voice_engine.speak("正在触发紧急呼叫，请保持冷静")
        
        # 显示确认弹窗
        self.show_emergency_confirm()
    
    def show_emergency_confirm(self):
        """显示紧急呼叫确认弹窗"""
        # 创建主容器
        main_content = BoxLayout(orientation='vertical', spacing=0)
        
        # 设置背景
        with main_content.canvas.before:
            Color(*get_color('background'))
            main_rect = Rectangle(size=main_content.size, pos=main_content.pos)
        
        def update_main_bg(instance, value):
            main_rect.size = instance.size
            main_rect.pos = instance.pos
        
        main_content.bind(size=update_main_bg, pos=update_main_bg)
        
        # 创建卡片式容器
        card_content = BoxLayout(orientation='vertical', spacing=20, padding=25)
        
        # 设置卡片背景
        with card_content.canvas.before:
            Color(*get_color('card'))
            card_rect = RoundedRectangle(size=card_content.size, pos=card_content.pos, radius=[DIMENSIONS['card_radius']])
        
        def update_card_bg(instance, value):
            card_rect.size = instance.size
            card_rect.pos = instance.pos
        
        card_content.bind(size=update_card_bg, pos=update_card_bg)
        
        # 标题
        title_label = Label(
            text='紧急呼叫确认',
            font_size=get_font_size('heading'),
            font_name='SimHei',
            bold=True,
            color=get_color('danger'),
            size_hint=(1, None),
            height=40,
            halign='center'
        )
        title_label.bind(size=title_label.setter('text_size'))
        card_content.add_widget(title_label)
        
        # 消息内容
        message = Label(
            text='确认触发紧急呼叫？\n\n系统将执行以下操作：\n1. 拨打所有紧急联系人\n2. 发送包含位置的求助短信',
            font_size=get_font_size('body'),
            font_name='SimHei',
            color=get_color('text_primary'),
            size_hint=(1, 0.6),
            halign='center',
            valign='middle'
        )
        message.bind(size=message.setter('text_size'))
        card_content.add_widget(message)
        
        # 位置信息
        if self.current_location and self.current_location.get('address'):
            location_str = self.current_location.get('address', '未知位置')
            location_label = Label(
                text=f'当前位置：{location_str}',
                font_size=get_font_size('caption'),
                font_name='SimHei',
                color=get_color('primary'),
                size_hint=(1, None),
                height=30,
                halign='center'
            )
            location_label.bind(size=location_label.setter('text_size'))
            card_content.add_widget(location_label)
        
        # 按钮容器
        buttons = BoxLayout(orientation='horizontal', size_hint=(1, 0.3),
                           spacing=20)
        
        # 取消按钮
        cancel_btn = Button(
            text='取消',
            font_size=get_font_size('button'),
            font_name='SimHei',
            background_color=get_color('secondary'),
            color=get_color('text_light'),
            size_hint=(0.5, 1),
            halign='center'
        )
        
        # 确认按钮
        confirm_btn = Button(
            text='确认呼叫',
            font_size=get_font_size('button'),
            font_name='SimHei',
            background_color=get_color('danger'),
            color=get_color('text_light'),
            size_hint=(0.5, 1),
            halign='center'
        )
        
        # 添加按钮到容器
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        card_content.add_widget(buttons)
        
        # 添加卡片到主容器
        main_content.add_widget(card_content)
        
        # 创建弹窗
        popup = Popup(
            title='',  # 标题已在卡片内
            content=main_content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False,
            background_color=(0, 0, 0, 0.5)  # 半透明背景
        )
        
        # 绑定按钮事件
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self.execute_emergency(popup))
        
        # 打开弹窗
        popup.open()
    
    def execute_emergency(self, popup):
        """执行紧急呼叫"""
        popup.dismiss()
        
        # 获取位置
        if not self.current_location:
            self.update_location()
        
        # 发送短信
        self.send_emergency_sms()
        
        # 呼叫联系人
        self.call_all_contacts()
        
        self.show_message('紧急呼叫已触发', 'warning')
    
    def send_emergency_sms(self):
        """发送紧急短信"""
        if not self.current_location:
            return
        
        message = f"紧急求助！我需要帮助。我的位置：{self.current_location.get('address', '未知')}"
        
        contacts = self.get_contacts()
        for contact in contacts:
            phone = contact.get('phone', '')
            if phone and self.community_service:
                try:
                    self.community_service.send_emergency_sms(phone, message, self.current_location)
                except:
                    pass
        
        if self.voice_engine:
            self.voice_engine.speak("已发送紧急求助短信")
    
    def call_all_contacts(self):
        """呼叫所有联系人"""
        contacts = self.get_contacts()
        
        if not contacts:
            if self.voice_engine:
                self.voice_engine.speak("没有设置紧急联系人")
            return
        
        for contact in contacts:
            phone = contact.get('phone', '')
            if phone and self.community_service:
                try:
                    self.community_service.call_emergency(
                        contact.get('name', ''), 
                        phone, 
                        self.current_location
                    )
                except:
                    pass
        
        if self.voice_engine:
            self.voice_engine.speak("正在呼叫紧急联系人")
    
    def call_contact(self, contact):
        """呼叫单个联系人"""
        phone = contact.get('phone', '')
        name = contact.get('name', '')
        
        if phone and self.community_service:
            try:
                self.community_service.call_emergency(name, phone, self.current_location)
                if self.voice_engine:
                    self.voice_engine.speak(f"正在呼叫{name}")
                # 显示呼叫反馈
                self.show_message(f'正在呼叫{name}\n电话：{phone}', 'info')
            except Exception as e:
                print(f"呼叫{name}失败: {e}")
                self.show_message(f'呼叫{name}失败', 'error')
                pass
    
    def call_number(self, number, name):
        """呼叫指定号码"""
        if self.community_service:
            try:
                self.community_service.call_emergency(name, number, self.current_location)
                if self.voice_engine:
                    self.voice_engine.speak(f"正在呼叫{name}")
                # 显示呼叫反馈
                self.show_message(f'正在呼叫{name}\n电话：{number}', 'info')
            except Exception as e:
                print(f"呼叫{name}失败: {e}")
                self.show_message(f'呼叫{name}失败', 'error')
                pass
    
    def get_contacts(self):
        """获取联系人列表"""
        if self.db_manager:
            try:
                db_contacts = self.db_manager.get_emergency_contacts()
                # 将数据库返回的元组转换为字典
                contacts = []
                for contact in db_contacts:
                    contact_dict = {
                        'id': contact[0],
                        'user_id': contact[1],
                        'contact_type': contact[2],
                        'name': contact[3],
                        'phone': contact[4],
                        'relation': contact[5]
                    }
                    contacts.append(contact_dict)
                return contacts
            except Exception as e:
                print(f"获取联系人失败: {e}")
                pass
        
        # 默认联系人
        return [
            {'name': '儿子', 'relation': '亲属', 'phone': '13800138000'},
            {'name': '女儿', 'relation': '亲属', 'phone': '13900139000'},
            {'name': '社区医生', 'relation': '医生', 'phone': '01012345678'},
        ]
    
    def load_contacts(self):
        """加载联系人列表"""
        self.contacts_list.clear_widgets()
        
        contacts = self.get_contacts()
        
        for contact in contacts:
            item = self._create_contact_item(contact)
            self.contacts_list.add_widget(item)
    
    def add_contact(self, instance=None):
        """添加联系人"""
        if self.voice_engine:
            self.voice_engine.speak("添加紧急联系人")
        
        # 创建主容器
        main_content = BoxLayout(orientation='vertical', spacing=0)
        
        # 设置背景
        with main_content.canvas.before:
            Color(*get_color('background'))
            main_rect = Rectangle(size=main_content.size, pos=main_content.pos)
        
        def update_main_bg(instance, value):
            main_rect.size = instance.size
            main_rect.pos = instance.pos
        
        main_content.bind(size=update_main_bg, pos=update_main_bg)
        
        # 创建卡片式表单容器
        form_card = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # 设置卡片背景
        with form_card.canvas.before:
            Color(*get_color('card'))
            card_rect = RoundedRectangle(size=form_card.size, pos=form_card.pos, radius=[DIMENSIONS['card_radius']])
        
        def update_card_bg(instance, value):
            card_rect.size = instance.size
            card_rect.pos = instance.pos
        
        form_card.bind(size=update_card_bg, pos=update_card_bg)
        
        # 姓名输入
        name_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None), height=60)
        name_label = Label(
            text='姓名',
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=20,
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))
        name_input = TextInput(
            hint_text='请输入联系人姓名',
            font_size=get_font_size('body'),
            size_hint=(1, None),
            height=40,
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[10, 10]
        )
        name_layout.add_widget(name_label)
        name_layout.add_widget(name_input)
        form_card.add_widget(name_layout)
        
        # 关系输入
        relation_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None), height=60)
        relation_label = Label(
            text='关系',
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=20,
            halign='left'
        )
        relation_label.bind(size=relation_label.setter('text_size'))
        relation_input = TextInput(
            hint_text='如：儿子、女儿、社区医生',
            font_size=get_font_size('body'),
            size_hint=(1, None),
            height=40,
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[10, 10]
        )
        relation_layout.add_widget(relation_label)
        relation_layout.add_widget(relation_input)
        form_card.add_widget(relation_layout)
        
        # 电话输入
        phone_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None), height=60)
        phone_label = Label(
            text='电话号码',
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=20,
            halign='left'
        )
        phone_label.bind(size=phone_label.setter('text_size'))
        phone_input = TextInput(
            hint_text='请输入手机号码',
            font_size=get_font_size('body'),
            size_hint=(1, None),
            height=40,
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[10, 10]
        )
        phone_layout.add_widget(phone_label)
        phone_layout.add_widget(phone_input)
        form_card.add_widget(phone_layout)
        
        # 按钮
        buttons = BoxLayout(orientation='horizontal', size_hint=(1, None),
                           height=50, spacing=15)
        
        # 取消按钮
        cancel_btn = Button(
            text='取消',
            font_size=get_font_size('button'),
            background_color=get_color('secondary'),
            color=get_color('text_light'),
            size_hint=(0.5, 1)
        )
        
        # 保存按钮
        save_btn = Button(
            text='保存',
            font_size=get_font_size('button'),
            background_color=get_color('success'),
            color=get_color('text_light'),
            size_hint=(0.5, 1)
        )
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(save_btn)
        form_card.add_widget(buttons)
        
        main_content.add_widget(form_card)
        
        popup = Popup(
            title='添加紧急联系人',
            content=main_content,
            size_hint=(0.85, 0.6),
            auto_dismiss=False,
            title_size=get_font_size('heading'),
            title_color=get_color('text_primary')
        )
        
        def save_contact(instance):
            try:
                name = name_input.text.strip()
                relation = relation_input.text.strip()
                phone = phone_input.text.strip()
                
                if not name or not phone:
                    self.show_message('请填写姓名和电话', 'warning')
                    return
                
                print(f"准备添加联系人: {name}, {relation}, {phone}")
                
                if self.db_manager:
                    try:
                        print("调用数据库添加方法")
                        self.db_manager.add_emergency_contact('紧急联系人', name, phone, relation)
                        print("数据库添加成功")
                    except Exception as e:
                        print(f"添加联系人失败: {e}")
                        # 即使数据库操作失败，也继续执行，避免程序崩溃
                
                print("关闭弹窗")
                popup.dismiss()
                
                print("重新加载联系人列表")
                self.load_contacts()
                
                print("显示成功消息")
                self.show_message('联系人添加成功', 'success')
                
                if self.voice_engine:
                    print("语音播报成功")
                    self.voice_engine.speak("联系人添加成功")
                    print("语音播报完成")
                
                print("添加联系人流程完成")
            except Exception as e:
                print(f"save_contact函数执行失败: {e}")
                import traceback
                traceback.print_exc()
                # 即使发生异常，也关闭弹窗，避免程序崩溃
                popup.dismiss()
                self.show_message('添加联系人时出现错误', 'error')
        
        cancel_btn.bind(on_press=popup.dismiss)
        save_btn.bind(on_press=save_contact)
        
        popup.open()
    
    def delete_contact(self, contact):
        """删除联系人"""
        if self.voice_engine:
            self.voice_engine.speak(f"删除联系人{contact.get('name', '')}")
        
        # 这里可以实现删除逻辑
        self.show_message('联系人删除功能开发中', 'info')
    
    def show_message(self, message, msg_type='info'):
        """显示消息弹窗"""
        colors = {
            'info': get_color('primary'),
            'success': get_color('success'),
            'warning': get_color('warning'),
            'error': get_color('danger')
        }
        
        # 创建主容器
        main_content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # 设置背景
        with main_content.canvas.before:
            Color(*get_color('background'))
            main_rect = Rectangle(size=main_content.size, pos=main_content.pos)
        
        def update_main_bg(instance, value):
            main_rect.size = instance.size
            main_rect.pos = instance.pos
        
        main_content.bind(size=update_main_bg, pos=update_main_bg)
        
        # 创建卡片式容器
        card_content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # 设置卡片背景
        with card_content.canvas.before:
            Color(*get_color('card'))
            card_rect = RoundedRectangle(size=card_content.size, pos=card_content.pos, radius=[DIMENSIONS['card_radius']])
        
        def update_card_bg(instance, value):
            card_rect.size = instance.size
            card_rect.pos = instance.pos
        
        card_content.bind(size=update_card_bg, pos=update_card_bg)
        
        # 标题
        title_label = Label(
            text='系统提示',
            font_size=get_font_size('heading'),
            font_name='SimHei',
            bold=True,
            color=colors.get(msg_type, get_color('text_primary')),
            size_hint=(1, None),
            height=40,
            halign='center'
        )
        title_label.bind(size=title_label.setter('text_size'))
        card_content.add_widget(title_label)
        
        # 消息内容
        message_label = Label(
            text=message,
            font_size=get_font_size('body'),
            font_name='SimHei',
            color=get_color('text_primary'),
            size_hint=(1, 0.6),
            halign='center',
            valign='middle'
        )
        message_label.bind(size=message_label.setter('text_size'))
        card_content.add_widget(message_label)
        
        # 添加额外信息（如果是紧急呼叫已触发）
        if message == '紧急呼叫已触发':
            # 显示联系人数量
            contacts = self.get_contacts()
            contact_count = len(contacts)
            
            # 显示位置信息
            location_str = '未知位置'
            if self.current_location and self.current_location.get('address'):
                location_str = self.current_location.get('address', '未知位置')
            
            # 附加信息
            extra_info = Label(
                text=f'已联系 {contact_count} 位紧急联系人\n当前位置：{location_str}',
                font_size=get_font_size('caption'),
                font_name='SimHei',
                color=get_color('text_secondary'),
                size_hint=(1, None),
                height=60,
                halign='center',
                valign='middle'
            )
            extra_info.bind(size=extra_info.setter('text_size'))
            card_content.add_widget(extra_info)
        
        # 确定按钮
        ok_button = Button(
            text='确定',
            font_size=get_font_size('button'),
            font_name='SimHei',
            background_color=colors.get(msg_type, get_color('primary')),
            color=get_color('text_light'),
            size_hint=(1, None),
            height=50,
            halign='center'
        )
        card_content.add_widget(ok_button)
        
        # 添加卡片到主容器
        main_content.add_widget(card_content)
        
        # 创建弹窗
        popup = Popup(
            title='',  # 标题已在卡片内
            content=main_content,
            size_hint=(0.85, 0.5),
            auto_dismiss=False,
            background_color=(0, 0, 0, 0.5)  # 半透明背景
        )
        
        # 绑定按钮事件
        ok_button.bind(on_press=popup.dismiss)
        
        # 打开弹窗
        popup.open()
        
        # 3秒后自动关闭
        Clock.schedule_once(lambda dt: popup.dismiss(), 5)
