"""
语音设置页面 - 使用统一UI样式
支持语速、音量、音色设置，语音播报开关等
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from screens.base_screen import BaseScreen
from styles import get_color, get_font_size, DIMENSIONS


class VoiceSettingsScreen(BaseScreen):
    name = StringProperty('voice_settings')
    
    # 设置文件路径
    SETTINGS_FILE = 'voice_settings.json'

    def __init__(self, voice_engine, app, **kwargs):
        self.title = '语音设置'
        super().__init__(voice_engine, app, **kwargs)
        
        # 默认设置
        self.settings = {
            'enabled': True,
            'rate': 50,  # 语速 0-100
            'volume': 80,  # 音量 0-100
            'voice_type': '女声',  # 女声/男声/童声
            'auto_read': True,  # 自动播报
            'read_notifications': True,  # 播报通知
            'read_buttons': True,  # 播报按钮
        }
        
        self.build_ui()
        Clock.schedule_once(lambda dt: self.load_settings(), 0.5)

    def build_ui(self):
        """构建语音设置界面"""
        super().build_ui()

        content = BoxLayout(orientation='vertical', spacing=15, padding=15)

        # 语音开关卡片
        enable_card = self.create_card(orientation='horizontal', size_hint=(1, None),
                                       height=70, padding=15, spacing=10)
        
        enable_label = Label(
            text='语音播报',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('text_primary'),
            size_hint=(0.7, 1),
            halign='left'
        )
        enable_label.bind(size=enable_label.setter('text_size'))
        enable_card.add_widget(enable_label)
        
        self.enable_switch = Switch(
            active=True,
            size_hint=(0.3, 1)
        )
        self.enable_switch.bind(active=self.on_enable_changed)
        enable_card.add_widget(self.enable_switch)
        
        content.add_widget(enable_card)

        # 语速设置卡片
        rate_card = self.create_card(orientation='vertical', size_hint=(1, None),
                                     height=130, padding=15, spacing=10)

        rate_header = BoxLayout(orientation='horizontal', size_hint=(1, None), height=30)
        rate_title = Label(
            text='语速',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(0.7, 1),
            halign='left'
        )
        rate_title.bind(size=rate_title.setter('text_size'))
        rate_header.add_widget(rate_title)
        
        self.rate_value_label = Label(
            text='50%',
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('primary'),
            size_hint=(0.3, 1),
            halign='right'
        )
        self.rate_value_label.bind(size=self.rate_value_label.setter('text_size'))
        rate_header.add_widget(self.rate_value_label)
        rate_card.add_widget(rate_header)

        rate_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
        rate_label_slow = Label(text='慢', font_size=get_font_size('body'),
                                color=get_color('text_secondary'), size_hint=(0.1, 1))
        self.rate_slider = Slider(min=0, max=100, value=50, size_hint=(0.8, 1))
        self.rate_slider.bind(value=self.on_rate_changed)
        rate_label_fast = Label(text='快', font_size=get_font_size('body'),
                                color=get_color('text_secondary'), size_hint=(0.1, 1))
        rate_layout.add_widget(rate_label_slow)
        rate_layout.add_widget(self.rate_slider)
        rate_layout.add_widget(rate_label_fast)
        rate_card.add_widget(rate_layout)

        content.add_widget(rate_card)

        # 音量设置卡片
        volume_card = self.create_card(orientation='vertical', size_hint=(1, None),
                                       height=130, padding=15, spacing=10)

        volume_header = BoxLayout(orientation='horizontal', size_hint=(1, None), height=30)
        volume_title = Label(
            text='音量',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(0.7, 1),
            halign='left'
        )
        volume_title.bind(size=volume_title.setter('text_size'))
        volume_header.add_widget(volume_title)
        
        self.volume_value_label = Label(
            text='80%',
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('primary'),
            size_hint=(0.3, 1),
            halign='right'
        )
        self.volume_value_label.bind(size=self.volume_value_label.setter('text_size'))
        volume_header.add_widget(self.volume_value_label)
        volume_card.add_widget(volume_header)

        volume_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
        volume_label_low = Label(text='小', font_size=get_font_size('body'),
                                 color=get_color('text_secondary'), size_hint=(0.1, 1))
        self.volume_slider = Slider(min=0, max=100, value=80, size_hint=(0.8, 1))
        self.volume_slider.bind(value=self.on_volume_changed)
        volume_label_high = Label(text='大', font_size=get_font_size('body'),
                                  color=get_color('text_secondary'), size_hint=(0.1, 1))
        volume_layout.add_widget(volume_label_low)
        volume_layout.add_widget(self.volume_slider)
        volume_layout.add_widget(volume_label_high)
        volume_card.add_widget(volume_layout)

        content.add_widget(volume_card)

        # 音色选择卡片
        voice_card = self.create_card(orientation='vertical', size_hint=(1, None),
                                      height=120, padding=15, spacing=10)

        voice_title = Label(
            text='音色',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=30,
            halign='left'
        )
        voice_title.bind(size=voice_title.setter('text_size'))
        voice_card.add_widget(voice_title)

        self.voice_spinner, spinner_layout = self.create_spinner(
            text='女声',
            values=('女声', '男声', '童声'),
            size_hint=(1, None),
            height=50
        )
        self.voice_spinner.bind(text=self.on_voice_type_changed)
        voice_card.add_widget(spinner_layout)

        content.add_widget(voice_card)

        # 高级设置卡片
        advanced_card = self.create_card(orientation='vertical', size_hint=(1, None),
                                         height=180, padding=15, spacing=10)

        advanced_title = Label(
            text='高级设置',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=30,
            halign='left'
        )
        advanced_title.bind(size=advanced_title.setter('text_size'))
        advanced_card.add_widget(advanced_title)

        # 自动播报
        auto_read_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
        auto_read_label = Label(
            text='自动播报页面内容',
            font_size=get_font_size('body'),
            color=get_color('text_primary'),
            size_hint=(0.7, 1),
            halign='left'
        )
        auto_read_label.bind(size=auto_read_label.setter('text_size'))
        auto_read_layout.add_widget(auto_read_label)
        
        self.auto_read_switch = Switch(active=True, size_hint=(0.3, 1))
        self.auto_read_switch.bind(active=self.on_auto_read_changed)
        auto_read_layout.add_widget(self.auto_read_switch)
        advanced_card.add_widget(auto_read_layout)

        # 播报通知
        notif_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
        notif_label = Label(
            text='播报社区通知',
            font_size=get_font_size('body'),
            color=get_color('text_primary'),
            size_hint=(0.7, 1),
            halign='left'
        )
        notif_label.bind(size=notif_label.setter('text_size'))
        notif_layout.add_widget(notif_label)
        
        self.notif_switch = Switch(active=True, size_hint=(0.3, 1))
        self.notif_switch.bind(active=self.on_notif_changed)
        notif_layout.add_widget(self.notif_switch)
        advanced_card.add_widget(notif_layout)

        content.add_widget(advanced_card)

        # 测试按钮
        test_btn = self.create_button(
            text='测试语音',
            color_key='primary',
            size_hint=(1, None),
            height=55,
            on_press=self.test_voice
        )
        content.add_widget(test_btn)

        # 保存按钮
        save_btn = self.create_button(
            text='保存设置',
            color_key='success',
            size_hint=(1, None),
            height=55,
            on_press=self.save_settings
        )
        content.add_widget(save_btn)

        # 提示信息
        tip_card = self.create_card(orientation='vertical', size_hint=(1, None),
                                    height=100, padding=15)

        tip_label = Label(
            text='提示：调整语速和音量可以让语音播报更加清晰舒适。\n建议根据您的听力情况选择合适的设置。',
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, 1)
        )
        tip_card.add_widget(tip_label)
        content.add_widget(tip_card)

        self.content_area.add_widget(content)

    def on_enable_changed(self, instance, value):
        """语音开关变化"""
        self.settings['enabled'] = value
        if self.voice_engine:
            status = '开启' if value else '关闭'
            self.voice_engine.speak(f'语音播报已{status}')

    def on_rate_changed(self, instance, value):
        """语速变化"""
        self.settings['rate'] = int(value)
        self.rate_value_label.text = f'{int(value)}%'

    def on_volume_changed(self, instance, value):
        """音量变化"""
        self.settings['volume'] = int(value)
        self.volume_value_label.text = f'{int(value)}%'

    def on_voice_type_changed(self, instance, value):
        """音色变化"""
        self.settings['voice_type'] = value
        if self.voice_engine:
            self.voice_engine.speak(f'已选择{value}')

    def on_auto_read_changed(self, instance, value):
        """自动播报变化"""
        self.settings['auto_read'] = value

    def on_notif_changed(self, instance, value):
        """通知播报变化"""
        self.settings['read_notifications'] = value

    def test_voice(self, instance=None):
        """测试语音"""
        if self.voice_engine and self.settings['enabled']:
            test_text = f"这是语音测试，当前语速{self.settings['rate']}%，音量{self.settings['volume']}%，音色为{self.settings['voice_type']}。"
            self.voice_engine.speak(test_text)
        elif not self.settings['enabled']:
            self.show_message('请先开启语音播报', 'warning')

    def save_settings(self, instance=None):
        """保存设置"""
        try:
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            
            # 应用设置到语音引擎
            if self.voice_engine:
                self.voice_engine.set_rate(self.settings['rate'])
                self.voice_engine.set_volume(self.settings['volume'])
                if self.settings['enabled']:
                    self.voice_engine.speak('设置已保存')
            
            self.show_message('设置保存成功', 'success')
        except Exception as e:
            self.show_message(f'保存失败: {str(e)}', 'error')

    def load_settings(self):
        """加载设置"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
        except Exception as e:
            print(f'加载设置失败: {e}')
        
        # 更新UI
        self.enable_switch.active = self.settings['enabled']
        self.rate_slider.value = self.settings['rate']
        self.volume_slider.value = self.settings['volume']
        self.voice_spinner.text = self.settings['voice_type']
        self.auto_read_switch.active = self.settings['auto_read']
        self.notif_switch.active = self.settings['read_notifications']
        
        self.rate_value_label.text = f"{self.settings['rate']}%"
        self.volume_value_label.text = f"{self.settings['volume']}%"

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
        
        Clock.schedule_once(lambda dt: popup.dismiss(), 3)
