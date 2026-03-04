from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from styles import get_color, get_font_size, DIMENSIONS


class HealthDetailScreen(Screen):
    name = StringProperty('health_detail')
    
    def __init__(self, voice_engine, db_manager, app, **kwargs):
        super().__init__(**kwargs)
        self.voice_engine = voice_engine
        self.db_manager = db_manager
        self.app = app
        self.records = []
        
        self.build_ui()
    
    def build_ui(self):
        """构建健康记录详情界面"""
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        with main_layout.canvas.before:
            Color(*get_color('background'))
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self.update_bg, pos=self.update_bg)
        
        # 标题栏
        header = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), padding=[10, 5])
        with header.canvas.before:
            Color(*get_color('success'))
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        header.bind(size=self.update_header, pos=self.update_header)
        
        back_btn = Button(
            text='返回',
            size_hint=(0.2, 1),
            background_color=(0, 0, 0, 0),
            color=get_color('text_light'),
            font_size=get_font_size('body')
        )
        back_btn.bind(on_press=self.go_back)
        
        title_label = Label(
            text='所有健康记录',
            size_hint=(0.6, 1),
            font_size=get_font_size('title'),
            bold=True,
            color=get_color('text_light')
        )
        
        header.add_widget(back_btn)
        header.add_widget(title_label)
        header.add_widget(Label(size_hint=(0.2, 1)))
        
        main_layout.add_widget(header)
        
        # 统计信息区域
        stats_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.12), 
                                  padding=[15, 10], spacing=10)
        
        self.stats_card = BoxLayout(orientation='vertical')
        with self.stats_card.canvas.before:
            Color(*get_color('card'))
            self.stats_rect = RoundedRectangle(size=self.stats_card.size, pos=self.stats_card.pos,
                                                radius=[DIMENSIONS['card_radius']])
        self.stats_card.bind(size=self.update_stats, pos=self.update_stats)
        
        self.stats_label = Label(
            text='共 0 条记录',
            font_size=get_font_size('body'),
            color=get_color('text_primary'),
            bold=True
        )
        self.stats_card.add_widget(self.stats_label)
        stats_layout.add_widget(self.stats_card)
        
        main_layout.add_widget(stats_layout)
        
        # 记录列表
        scroll_view = ScrollView(size_hint=(1, 0.68))
        
        self.records_layout = BoxLayout(orientation='vertical', spacing=10, 
                                        padding=[15, 10], size_hint_y=None)
        self.records_layout.bind(minimum_height=self.records_layout.setter('height'))
        
        scroll_view.add_widget(self.records_layout)
        main_layout.add_widget(scroll_view)
        
        # 底部按钮
        footer = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), 
                           padding=[15, 10], spacing=10)
        
        clear_btn = Button(
            text='清空记录',
            size_hint=(0.5, 1),
            background_color=get_color('danger'),
            color=get_color('text_light'),
            font_size=get_font_size('button'),
            bold=True
        )
        clear_btn.bind(on_press=self.clear_records)
        
        refresh_btn = Button(
            text='刷新',
            size_hint=(0.5, 1),
            background_color=get_color('primary'),
            color=get_color('text_light'),
            font_size=get_font_size('button'),
            bold=True
        )
        refresh_btn.bind(on_press=self.load_records)
        
        footer.add_widget(clear_btn)
        footer.add_widget(refresh_btn)
        main_layout.add_widget(footer)
        
        self.add_widget(main_layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    def update_header(self, instance, value):
        self.header_rect.size = instance.size
        self.header_rect.pos = instance.pos
    
    def update_stats(self, instance, value):
        self.stats_rect.size = instance.size
        self.stats_rect.pos = instance.pos
    
    def on_enter(self):
        """进入屏幕时加载记录"""
        self.load_records()
    
    def load_records(self, instance=None):
        """加载健康记录"""
        self.records_layout.clear_widgets()
        
        # 从数据库获取记录
        if self.db_manager:
            try:
                # 检查db_manager是否有get_all_health_records方法
                if hasattr(self.db_manager, 'get_all_health_records'):
                    records = self.db_manager.get_all_health_records()
                    self.records = []
                    
                    # 处理记录格式
                    for record in records:
                        try:
                            # 格式化日期
                            record_time = record[6]
                            try:
                                record_dt = datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
                                date_str = record_dt.strftime('%Y-%m-%d %H:%M')
                            except:
                                date_str = record_time
                            
                            # 创建记录字典
                            record_dict = {
                                'date': date_str,
                                'type': record[2],
                                'value': f"{record[3]} {record[4]}",
                                'note': record[5] if record[5] else '无'
                            }
                            self.records.append(record_dict)
                        except Exception as e:
                            print(f"处理记录失败: {e}")
                            continue
                else:
                    print("数据库管理器没有get_all_health_records方法")
                    self.records = []
            except Exception as e:
                print(f"获取健康记录失败: {e}")
                self.records = []
        else:
            # 模拟数据
            self.records = [
                {'date': '2024-01-15', 'type': '血压', 'value': '120/80 mmHg', 'note': '正常'},
                {'date': '2024-01-14', 'type': '血糖', 'value': '5.6 mmol/L', 'note': '空腹'},
                {'date': '2024-01-13', 'type': '体重', 'value': '65.5 kg', 'note': '早晨'},
            ]
        
        # 更新统计
        self.stats_label.text = f'共 {len(self.records)} 条记录'
        
        if not self.records:
            # 显示空状态
            empty_label = Label(
                text='暂无健康记录\n\n快去添加您的第一条记录吧！',
                font_size=get_font_size('body'),
                color=get_color('text_secondary'),
                size_hint_y=None,
                height=200
            )
            self.records_layout.add_widget(empty_label)
        else:
            # 显示记录列表
            for record in self.records:
                record_card = self.create_record_card(record)
                self.records_layout.add_widget(record_card)
    
    def create_record_card(self, record):
        """创建记录卡片"""
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=120, 
                         padding=[15, 10])
        with card.canvas.before:
            Color(*get_color('card'))
            RoundedRectangle(size=card.size, pos=card.pos, 
                            radius=[DIMENSIONS['card_radius']])
        card.bind(size=self.update_card, pos=self.update_card)
        
        # 日期和类型
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.4))
        
        date_label = Label(
            text=record.get('date', ''),
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(0.5, 1),
            halign='left'
        )
        date_label.bind(size=date_label.setter('text_size'))
        
        type_label = Label(
            text=record.get('type', ''),
            font_size=get_font_size('body'),
            color=get_color('primary'),
            bold=True,
            size_hint=(0.5, 1),
            halign='right'
        )
        type_label.bind(size=type_label.setter('text_size'))
        
        header_layout.add_widget(date_label)
        header_layout.add_widget(type_label)
        
        # 数值
        value_label = Label(
            text=record.get('value', ''),
            font_size=get_font_size('heading'),
            color=get_color('text_primary'),
            bold=True,
            size_hint=(1, 0.35)
        )
        
        # 备注
        note_label = Label(
            text=record.get('note', ''),
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, 0.25),
            halign='left'
        )
        note_label.bind(size=note_label.setter('text_size'))
        
        card.add_widget(header_layout)
        card.add_widget(value_label)
        card.add_widget(note_label)
        
        return card
    
    def update_card(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*get_color('card'))
            RoundedRectangle(size=instance.size, pos=instance.pos, 
                            radius=[DIMENSIONS['card_radius']])
    
    def clear_records(self, instance):
        """清空所有记录"""
        if self.db_manager:
            try:
                # 检查db_manager是否有clear_health_records方法
                if hasattr(self.db_manager, 'clear_health_records'):
                    self.db_manager.clear_health_records()
                    if self.voice_engine:
                        self.voice_engine.speak('已清空所有健康记录')
                else:
                    print("数据库管理器没有clear_health_records方法")
            except Exception as e:
                print(f"清空记录失败: {e}")
        
        self.load_records()
    
    def go_back(self, instance):
        """返回健康记录页面"""
        self.app.screen_manager.current = 'health'
