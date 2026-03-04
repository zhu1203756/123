"""
健康记录页面 - 使用统一UI样式
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from screens.base_screen import BaseScreen
from styles import get_color, get_font_size, DIMENSIONS


class HealthScreen(BaseScreen):
    name = StringProperty('health')
    
    def __init__(self, voice_engine, db_manager, app, **kwargs):
        self.title = '健康记录'
        super().__init__(voice_engine, app, **kwargs)
        self.db_manager = db_manager
        
        self.unit_mapping = {
            '血压': ['mmHg', 'kPa'],
            '血糖': ['mmol/L', 'mg/dL'],
            '心率': ['次/分', 'bpm'],
            '体温': ['℃', '℉'],
            '体重': ['kg', '斤'],
            '血氧': ['%']
        }
        
        self.build_ui()
        Clock.schedule_once(lambda dt: self.refresh_records(), 0.5)
    
    def build_ui(self):
        """构建健康记录界面"""
        super().build_ui()
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        # 记录输入卡片
        input_card = self.create_card(orientation='vertical', size_hint=(1, 0.4),
                                      padding=15, spacing=10)
        
        input_title = Label(
            text='添加记录',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=35,
            halign='left'
        )
        input_title.bind(size=input_title.setter('text_size'))
        input_card.add_widget(input_title)
        
        # 类型和单位选择行
        select_layout = BoxLayout(orientation='horizontal', size_hint=(1, None),
                                  height=50, spacing=10)
        
        self.type_spinner, spinner_layout = self.create_spinner(
            text='选择类型',
            values=list(self.unit_mapping.keys()),
            size_hint=(0.5, 1)
        )
        self.type_spinner.bind(text=self.on_type_select)
        select_layout.add_widget(spinner_layout)
        
        self.unit_spinner, spinner_layout = self.create_spinner(
            text='单位',
            values=[],
            size_hint=(0.5, 1)
        )
        select_layout.add_widget(spinner_layout)
        
        input_card.add_widget(select_layout)
        
        # 数值输入行
        value_layout = BoxLayout(orientation='horizontal', size_hint=(1, None),
                                 height=50, spacing=10)
        
        self.value_input = TextInput(
            hint_text='输入数值',
            font_size=get_font_size('body'),
            size_hint=(0.6, 1),
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[10, 10]
        )
        value_layout.add_widget(self.value_input)
        
        add_btn = self.create_button(
            text='添加记录',
            color_key='success',
            size_hint=(0.4, 1),
            on_press=self.add_record
        )
        value_layout.add_widget(add_btn)
        
        input_card.add_widget(value_layout)
        
        # 备注输入
        note_label = Label(
            text='备注（选填）',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=25,
            halign='left'
        )
        note_label.bind(size=note_label.setter('text_size'))
        input_card.add_widget(note_label)
        
        self.note_input = TextInput(
            hint_text='添加备注信息',
            font_size=get_font_size('body'),
            size_hint=(1, None),
            height=60,
            multiline=True,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[10, 10]
        )
        input_card.add_widget(self.note_input)
        
        content.add_widget(input_card)
        
        # 历史记录卡片
        history_card = self.create_card(orientation='vertical', size_hint=(1, 0.48),
                                        padding=15, spacing=10)
        
        # 标题行
        history_header = BoxLayout(orientation='horizontal', size_hint=(1, None), height=35)
        
        history_title = Label(
            text='历史记录',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(0.6, 1),
            halign='left'
        )
        history_title.bind(size=history_title.setter('text_size'))
        
        view_all_btn = self.create_button(
            text='查看全部',
            color_key='primary',
            size_hint=(0.4, 1),
            on_press=self.view_all_records
        )
        
        history_header.add_widget(history_title)
        history_header.add_widget(view_all_btn)
        history_card.add_widget(history_header)
        
        # 记录列表
        history_scroll = ScrollView(size_hint=(1, 1))
        self.records_list = BoxLayout(orientation='vertical', size_hint=(1, None),
                                      spacing=8, padding=5)
        self.records_list.bind(minimum_height=self.records_list.setter('height'))
        
        history_scroll.add_widget(self.records_list)
        history_card.add_widget(history_scroll)
        
        content.add_widget(history_card)
        
        # 底部提示
        tip_label = Label(
            text='提示：定期记录健康数据有助于了解身体状况',
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=30
        )
        content.add_widget(tip_label)
        
        self.content_area.add_widget(content)
    
    def on_type_select(self, spinner, text):
        """类型选择回调"""
        if text in self.unit_mapping:
            self.unit_spinner.values = self.unit_mapping[text]
            if self.unit_spinner.values:
                self.unit_spinner.text = self.unit_spinner.values[0]
    
    def _create_record_item(self, record):
        """创建记录项"""
        row = BoxLayout(orientation='horizontal', size_hint=(1, None),
                       height=70, spacing=10, padding=8)
        
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
        
        # 类型名称
        type_name = Label(
            text=record.get('type', ''),
            font_size=get_font_size('body'),
            color=get_color('text_primary'),
            size_hint=(0.25, 1)
        )
        row.add_widget(type_name)
        
        # 数值
        value_label = Label(
            text=f"{record.get('value', '')} {record.get('unit', '')}",
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('primary'),
            size_hint=(0.35, 1)
        )
        row.add_widget(value_label)
        
        # 日期
        date_label = Label(
            text=record.get('date', ''),
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(0.25, 1)
        )
        row.add_widget(date_label)
        
        # 状态指示
        status_color = get_color('success') if record.get('normal', True) else get_color('warning')
        status_label = Label(
            text='',
            font_size=20,
            color=status_color,
            size_hint=(0.15, 1)
        )
        row.add_widget(status_label)
        
        return row
    
    def _get_type_icon(self, type_name):
        """获取类型图标"""
        icons = {
            '血压': '🩺',
            '血糖': '🍬',
            '心率': '💓',
            '体温': '🌡️',
            '体重': '⚖️',
            '血氧': '💨'
        }
        return icons.get(type_name, '📋')
    
    def _is_normal_value(self, record_type, value, unit):
        """判断健康记录是否在正常范围内"""
        try:
            # 转换值为浮点数
            if '/' in str(value):
                # 血压特殊处理
                systolic, diastolic = str(value).split('/')
                systolic = float(systolic)
                diastolic = float(diastolic)
                return 90 <= systolic <= 140 and 60 <= diastolic <= 90
            else:
                value = float(value)
        except:
            return True
        
        # 不同类型的正常范围
        normal_ranges = {
            '血糖': {'mmol/L': (3.9, 6.1), 'mg/dL': (70, 110)},
            '心率': {'次/分': (60, 100), 'bpm': (60, 100)},
            '体温': {'℃': (36.3, 37.3), '℉': (97.3, 99.1)},
            '血氧': {'%': (95, 100)}
        }
        
        if record_type in normal_ranges and unit in normal_ranges[record_type]:
            min_val, max_val = normal_ranges[record_type][unit]
            return min_val <= value <= max_val
        
        return True
    
    def add_record(self):
        """添加记录"""
        record_type = self.type_spinner.text
        if record_type == '选择类型':
            self.voice_engine.speak("请先选择记录类型")
            return
        
        value = self.value_input.text.strip()
        if not value:
            self.voice_engine.speak("请输入数值")
            return
        
        unit = self.unit_spinner.text
        note = self.note_input.text.strip()
        
        # 保存到数据库
        try:
            self.db_manager.add_health_record(record_type, value, unit, note)
            self.voice_engine.speak(f"已添加{record_type}记录")
        except Exception as e:
            self.voice_engine.speak("保存记录失败")
            print(f"保存健康记录失败: {e}")
        
        # 清空输入
        self.value_input.text = ''
        self.note_input.text = ''
        
        # 刷新记录列表
        self.refresh_records()
    
    def refresh_records(self):
        """刷新记录列表"""
        self.records_list.clear_widgets()
        
        # 从数据库获取记录
        try:
            records = self.db_manager.get_health_records(limit=5)
            
            if not records:
                # 如果没有记录，显示提示
                empty_label = Label(
                    text='暂无健康记录',
                    font_size=get_font_size('body'),
                    color=get_color('text_secondary'),
                    size_hint=(1, None),
                    height=50
                )
                self.records_list.add_widget(empty_label)
            else:
                # 处理并显示记录
                for record in records:
                    # 格式化日期
                    record_time = record[6]
                    import datetime
                    try:
                        record_dt = datetime.datetime.strptime(record_time, '%Y-%m-%d %H:%M:%S')
                        today = datetime.date.today()
                        record_date = record_dt.date()
                        
                        if record_date == today:
                            date_str = f'今天 {record_dt.strftime("%H:%M")}'
                        elif record_date == today - datetime.timedelta(days=1):
                            date_str = f'昨天 {record_dt.strftime("%H:%M")}'
                        else:
                            date_str = record_dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        date_str = record_time
                    
                    # 创建记录字典
                    record_dict = {
                        'type': record[2],
                        'value': str(record[3]),
                        'unit': record[4],
                        'date': date_str,
                        'normal': self._is_normal_value(record[2], record[3], record[4])
                    }
                    
                    # 创建记录项并添加到列表
                    record_item = self._create_record_item(record_dict)
                    self.records_list.add_widget(record_item)
        except Exception as e:
            print(f"获取健康记录失败: {e}")
            # 显示错误提示
            error_label = Label(
                text='获取记录失败',
                font_size=get_font_size('body'),
                color=get_color('danger'),
                size_hint=(1, None),
                height=50
            )
            self.records_list.add_widget(error_label)
    
    def view_all_records(self, instance=None):
        """查看所有记录"""
        if self.voice_engine:
            self.voice_engine.speak('查看所有健康记录')
        self.app.screen_manager.current = 'health_detail'
