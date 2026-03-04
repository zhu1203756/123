"""
社区通知页面 - 使用统一UI样式
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from screens.base_screen import BaseScreen
from styles import get_color, get_font_size, DIMENSIONS
from database import get_db_connection, close_db_connection


class NotificationScreen(BaseScreen):
    name = StringProperty('notification')
    
    def __init__(self, voice_engine, community_service, db_manager, app, **kwargs):
        self.title = '社区通知'
        super().__init__(voice_engine, app, **kwargs)
        self.community_service = community_service
        self.db_manager = db_manager
        
        self.build_ui()
        Clock.schedule_once(lambda dt: self.refresh_notifications(), 0.5)
    
    def build_ui(self):
        """构建通知界面"""
        super().build_ui()
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        # 分类标签
        category_bar = BoxLayout(orientation='horizontal', size_hint=(1, None),
                                 height=50, spacing=10)
        
        self.category_buttons = []
        categories = [
            {'name': '全部', 'key': 'all'},
            {'name': '社区', 'key': 'community'},
            {'name': '紧急', 'key': 'urgent'},
            {'name': '活动', 'key': 'activity'}
        ]
        
        for cat in categories:
            btn = self._create_category_tab(cat['name'], cat['key'])
            category_bar.add_widget(btn)
            self.category_buttons.append((btn, cat['key']))
        
        # 默认选中"全部"
        self.current_category = 'all'
        self._update_category_buttons()
        
        content.add_widget(category_bar)
        
        # 通知列表卡片
        list_card = self.create_card(orientation='vertical', size_hint=(1, 0.75),
                                     padding=15, spacing=10)
        
        # 标题行
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, None),
                                  height=40, spacing=10)
        
        list_title = Label(
            text='通知列表',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(0.7, 1),
            halign='left'
        )
        list_title.bind(size=list_title.setter('text_size'))
        header_layout.add_widget(list_title)
        
        # 未读数量
        self.unread_label = Label(
            text='未读: 0',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(0.3, 1),
            halign='right'
        )
        self.unread_label.bind(size=self.unread_label.setter('text_size'))
        header_layout.add_widget(self.unread_label)
        
        list_card.add_widget(header_layout)
        
        # 通知列表
        list_scroll = ScrollView(size_hint=(1, 1))
        self.notification_list = BoxLayout(orientation='vertical', size_hint=(1, None),
                                           spacing=10, padding=5)
        self.notification_list.bind(minimum_height=self.notification_list.setter('height'))
        
        list_scroll.add_widget(self.notification_list)
        list_card.add_widget(list_scroll)
        
        content.add_widget(list_card)
        
        # 底部操作栏
        action_bar = BoxLayout(orientation='horizontal', size_hint=(1, None),
                               height=60, spacing=15, padding=[0, 5])
        
        # 标记全部已读
        read_all_btn = self.create_button(
            text='全部已读',
            color_key='secondary',
            size_hint=(0.5, 1),
            on_press=lambda x: self.mark_all_read()
        )
        action_bar.add_widget(read_all_btn)
        
        # 刷新按钮
        refresh_btn = self.create_button(
            text='刷新',
            color_key='primary',
            size_hint=(0.5, 1),
            on_press=lambda x: self.refresh_notifications()
        )
        action_bar.add_widget(refresh_btn)
        
        content.add_widget(action_bar)
        
        self.content_area.add_widget(content)
    
    def _create_category_tab(self, name, key):
        """创建分类标签"""
        btn = BoxLayout(orientation='vertical', size_hint=(1, 1))
        
        label = Label(
            text=name,
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('text_secondary'),
            size_hint=(1, 1)
        )
        btn.add_widget(label)
        
        # 下划线指示器
        indicator = BoxLayout(size_hint=(1, None), height=3)
        btn.add_widget(indicator)
        
        btn.bind(on_touch_down=lambda instance, touch, k=key:
                 self.select_category(k) if instance.collide_point(*touch.pos) else None)
        
        btn.label = label
        btn.indicator = indicator
        btn.key = key
        
        return btn
    
    def _update_category_buttons(self):
        """更新分类按钮状态"""
        for btn, key in self.category_buttons:
            if key == self.current_category:
                btn.label.color = get_color('primary')
                btn.label.bold = True
                with btn.indicator.canvas.before:
                    btn.indicator.canvas.before.clear()
                    Color(*get_color('primary'))
                    RoundedRectangle(size=btn.indicator.size, pos=btn.indicator.pos,
                                   radius=[2])
            else:
                btn.label.color = get_color('text_secondary')
                btn.label.bold = False
                btn.indicator.canvas.before.clear()
    
    def select_category(self, category):
        """选择分类"""
        self.current_category = category
        self._update_category_buttons()
        self.refresh_notifications()
    
    def _create_notification_item(self, notification):
        """创建通知项"""
        is_urgent = notification.get('type') == 'urgent'
        is_unread = not notification.get('read', False)
        
        row = BoxLayout(orientation='horizontal', size_hint=(1, None),
                       height=90, spacing=10, padding=12)
        
        # 背景色
        bg_color = get_color('warning') if is_urgent else get_color('background')
        bg_color = (*bg_color[:3], 0.2 if is_urgent else 1)
        
        with row.canvas.before:
            Color(*bg_color)
            RoundedRectangle(size=row.size, pos=row.pos,
                           radius=[DIMENSIONS['card_radius']])
        
        def update_row(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*bg_color)
                RoundedRectangle(size=instance.size, pos=instance.pos,
                               radius=[DIMENSIONS['card_radius']])
        
        row.bind(size=update_row, pos=update_row)
        
        # 左侧指示条
        indicator_color = get_color('danger') if is_urgent else (
            get_color('primary') if is_unread else get_color('divider')
        )
        indicator = BoxLayout(size_hint=(None, 1), width=4)
        with indicator.canvas.before:
            Color(*indicator_color)
            RoundedRectangle(size=indicator.size, pos=indicator.pos,
                           radius=[2])
        indicator.bind(size=lambda i, v: setattr(i.canvas.before.children[-1], 'size', i.size),
                      pos=lambda i, v: setattr(i.canvas.before.children[-1], 'pos', i.pos))
        row.add_widget(indicator)
        
        # 内容区域
        content_layout = BoxLayout(orientation='vertical', size_hint=(0.75, 1))
        
        # 标题行
        title_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        
        # 类型标签
        type_icon = ''
        type_label = Label(
            text=f"{type_icon} {notification.get('type_name', '通知')}",
            font_size=get_font_size('caption'),
            color=get_color('danger') if is_urgent else get_color('primary'),
            size_hint=(0.4, 1),
            halign='left'
        )
        type_label.bind(size=type_label.setter('text_size'))
        title_layout.add_widget(type_label)
        
        # 时间
        time_label = Label(
            text=notification.get('time', ''),
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(0.6, 1),
            halign='right'
        )
        time_label.bind(size=time_label.setter('text_size'))
        title_layout.add_widget(time_label)
        
        content_layout.add_widget(title_layout)
        
        # 标题
        title_text = notification.get('title', '')
        if is_unread:
            title_text = '● ' + title_text
        
        title = Label(
            text=title_text,
            font_size=get_font_size('body'),
            bold=is_unread,
            color=get_color('text_primary'),
            size_hint=(1, 0.5),
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        content_layout.add_widget(title)
        
        row.add_widget(content_layout)
        
        # 查看按钮
        view_btn = self.create_button(
            text='查看',
            color_key='primary' if is_unread else 'secondary',
            size_hint=(0.2, 1),
            on_press=lambda x: self.view_notification(notification)
        )
        row.add_widget(view_btn)
        
        return row
    
    def view_notification(self, notification):
        """查看通知详情"""
        self.voice_engine.speak(notification.get('title', '通知'))
        # 标记为已读
        notification['read'] = True
        
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
            text=notification.get('title', '通知'),
            font_size=get_font_size('heading'),
            font_name='SimHei',
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=40,
            halign='center'
        )
        title_label.bind(size=title_label.setter('text_size'))
        card_content.add_widget(title_label)
        
        # 类型和时间
        info_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=30)
        type_label = Label(
            text=f"类型：{notification.get('type_name', '通知')}",
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(0.5, 1),
            halign='left'
        )
        type_label.bind(size=type_label.setter('text_size'))
        time_label = Label(
            text=f"时间：{notification.get('time', '')}",
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(0.5, 1),
            halign='right'
        )
        time_label.bind(size=time_label.setter('text_size'))
        info_layout.add_widget(type_label)
        info_layout.add_widget(time_label)
        card_content.add_widget(info_layout)
        
        # 内容
        content_label = Label(
            text=notification.get('content', '无内容'),
            font_size=get_font_size('body'),
            font_name='SimHei',
            color=get_color('text_primary'),
            size_hint=(1, 0.6),
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        content_label.bind(size=content_label.setter('text_size'))
        card_content.add_widget(content_label)
        
        # 确定按钮
        ok_button = Button(
            text='确定',
            font_size=get_font_size('button'),
            font_name='SimHei',
            background_color=get_color('primary'),
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
            size_hint=(0.85, 0.6),
            auto_dismiss=False,
            background_color=(0, 0, 0, 0.5)  # 半透明背景
        )
        
        # 绑定按钮事件
        ok_button.bind(on_press=popup.dismiss)
        
        # 打开弹窗
        popup.open()
        
        # 刷新通知列表
        self.refresh_notifications()
    
    def mark_all_read(self):
        """标记全部已读"""
        self.voice_engine.speak("已标记全部通知为已读")
        # 更新所有通知状态
        for notif in self.notifications:
            notif['read'] = True
        self.refresh_notifications()
    
    def refresh_notifications(self):
        """刷新通知列表"""
        self.notification_list.clear_widgets()
        
        # 保存当前已读状态
        current_read_status = {}
        if hasattr(self, 'notifications'):
            for notif in self.notifications:
                current_read_status[notif['id']] = notif.get('read', False)
        
        # 从数据库加载通知
        self.notifications = []
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, title, content, author, created_at FROM notices WHERE is_active = 1 ORDER BY created_at DESC')
                for row in cursor.fetchall():
                    # 计算时间差
                    created_at = datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S')
                    now = datetime.now()
                    delta = now - created_at
                    
                    if delta.days == 0:
                        if delta.seconds < 60:
                            time_str = f'{delta.seconds}秒前'
                        elif delta.seconds < 3600:
                            time_str = f'{delta.seconds//60}分钟前'
                        else:
                            time_str = f'{delta.seconds//3600}小时前'
                    elif delta.days == 1:
                        time_str = '昨天'
                    else:
                        time_str = f'{delta.days}天前'
                    
                    # 类型映射（默认社区类型）
                    notification_type = 'community'
                    
                    # 保持之前的已读状态
                    read_status = current_read_status.get(row[0], False)
                    
                    self.notifications.append({
                        'id': row[0],
                        'type': notification_type,
                        'type_name': '社区',
                        'title': row[1],
                        'content': row[2],
                        'author': row[3],
                        'time': time_str,
                        'read': read_status  # 使用之前的已读状态
                    })
                close_db_connection(conn)
        except Exception as e:
            print(f"加载通知失败: {e}")
        
        # 筛选通知
        filtered = self.notifications
        if self.current_category != 'all':
            filtered = [n for n in self.notifications if n['type'] == self.current_category]
        
        # 更新未读数量
        unread_count = sum(1 for n in self.notifications if not n.get('read', False))
        self.unread_label.text = f'未读: {unread_count}'
        
        # 添加到列表
        for notification in filtered:
            item = self._create_notification_item(notification)
            self.notification_list.add_widget(item)
