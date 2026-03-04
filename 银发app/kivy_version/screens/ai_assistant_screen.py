"""
AI助手页面 - 使用统一UI样式
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.graphics import Color, RoundedRectangle
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from screens.base_screen import BaseScreen
from styles import get_color, get_font_size, DIMENSIONS


class AIAssistantScreen(BaseScreen):
    name = StringProperty('ai_assistant')
    
    def __init__(self, voice_engine, ai_assistant, app, **kwargs):
        self.title = 'AI助手'
        super().__init__(voice_engine, app, **kwargs)
        self.ai_assistant = ai_assistant
        self.messages = []
        
        self.build_ui()
        self.add_message("AI", "您好！我是您的智能助手，有什么可以帮您的吗？")
    
    def build_ui(self):
        """构建 AI 助手界面"""
        super().build_ui()
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        # 聊天区域卡片
        chat_card = self.create_card(orientation='vertical', size_hint=(1, 0.75),
                                     padding=15, spacing=10)
        
        # 标题
        chat_title = Label(
            text='智能对话',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=35,
            halign='left'
        )
        chat_title.bind(size=chat_title.setter('text_size'))
        chat_card.add_widget(chat_title)
        
        # 消息列表
        chat_scroll = ScrollView(size_hint=(1, 1))
        self.message_list = BoxLayout(orientation='vertical', size_hint=(1, None),
                                      spacing=10, padding=5)
        self.message_list.bind(minimum_height=self.message_list.setter('height'))
        
        chat_scroll.add_widget(self.message_list)
        chat_card.add_widget(chat_scroll)
        
        content.add_widget(chat_card)
        
        # 快捷问题卡片
        quick_card = self.create_card(orientation='vertical', size_hint=(1, 0.18),
                                      padding=10, spacing=8)
        
        quick_title = Label(
            text='快捷问题',
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=25,
            halign='left'
        )
        quick_title.bind(size=quick_title.setter('text_size'))
        quick_card.add_widget(quick_title)
        
        # 快捷问题按钮行
        quick_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1),
                                 spacing=8)
        
        quick_questions = [
            '今天天气怎么样',
            '帮我订餐',
            '提醒吃药',
            '紧急求助'
        ]
        
        for question in quick_questions:
            btn = self._create_quick_button(question)
            quick_layout.add_widget(btn)
        
        quick_card.add_widget(quick_layout)
        content.add_widget(quick_card)
        
        # 输入区域
        input_bar = BoxLayout(orientation='horizontal', size_hint=(1, None),
                              height=60, spacing=10)
        
        self.message_input = TextInput(
            hint_text='输入您的问题...',
            font_size=get_font_size('body'),
            size_hint=(0.75, 1),
            multiline=False,
            background_color=get_color('background'),
            foreground_color=get_color('text_primary'),
            padding=[15, 15]
        )
        input_bar.add_widget(self.message_input)
        
        # 发送按钮
        send_btn = self.create_button(
            text='发送',
            color_key='success',
            size_hint=(0.15, 1),
            on_press=self.send_message
        )
        input_bar.add_widget(send_btn)
        
        # 语音按钮
        voice_btn = self.create_button(
            text='语音',
            color_key='primary',
            size_hint=(0.1, 1),
            on_press=self.start_voice_input
        )
        input_bar.add_widget(voice_btn)
        
        content.add_widget(input_bar)
        
        self.content_area.add_widget(content)
    
    def _create_quick_button(self, text):
        """创建快捷问题按钮"""
        btn = BoxLayout(orientation='vertical', size_hint=(1, 1))
        
        with btn.canvas.before:
            Color(*get_color('secondary_light'))
            RoundedRectangle(size=btn.size, pos=btn.pos,
                           radius=[DIMENSIONS['button_radius']])
        
        def update_btn(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*get_color('secondary_light'))
                RoundedRectangle(size=instance.size, pos=instance.pos,
                               radius=[DIMENSIONS['button_radius']])
        
        btn.bind(size=update_btn, pos=update_btn)
        
        label = Label(
            text=text,
            font_size=get_font_size('caption'),
            color=get_color('text_primary'),
            size_hint=(1, 1)
        )
        btn.add_widget(label)
        
        btn.bind(on_touch_down=lambda instance, touch, q=text:
                 self.ask_quick_question(q) if instance.collide_point(*touch.pos) else None)
        
        return btn
    
    def _create_message_bubble(self, sender, message, is_user=False):
        """创建消息气泡"""
        # 消息行
        row = BoxLayout(orientation='horizontal', size_hint=(1, None),
                       height=80, spacing=10, padding=5)
        
        # 头像
        avatar = Label(
            text='用户' if is_user else 'AI',
            font_size=14,
            size_hint=(0.1, 1)
        )
        
        if is_user:
            row.add_widget(BoxLayout(size_hint=(0.2, 1)))  # 左侧占位
        
        row.add_widget(avatar)
        
        # 气泡
        bubble = BoxLayout(orientation='vertical', size_hint=(0.6, 1),
                          padding=10)
        
        # 气泡背景
        bubble_color = get_color('primary_light') if is_user else get_color('background')
        with bubble.canvas.before:
            Color(*bubble_color)
            RoundedRectangle(size=bubble.size, pos=bubble.pos,
                           radius=[15])
        
        def update_bubble(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*bubble_color)
                RoundedRectangle(size=instance.size, pos=instance.pos,
                               radius=[15])
        
        bubble.bind(size=update_bubble, pos=update_bubble)
        
        # 消息文本
        msg_label = Label(
            text=message,
            font_size=get_font_size('body'),
            color=get_color('text_primary') if is_user else get_color('text_primary'),
            size_hint=(1, 1),
            halign='left',
            valign='center'
        )
        msg_label.bind(size=msg_label.setter('text_size'))
        bubble.add_widget(msg_label)
        
        row.add_widget(bubble)
        
        if not is_user:
            row.add_widget(BoxLayout(size_hint=(0.2, 1)))  # 右侧占位
        
        return row
    
    def add_message(self, sender, message):
        """添加消息到列表"""
        is_user = (sender == "用户")
        bubble = self._create_message_bubble(sender, message, is_user)
        self.message_list.add_widget(bubble)
        self.messages.append({'sender': sender, 'message': message})
    
    def send_message(self):
        """发送消息"""
        message = self.message_input.text.strip()
        if not message:
            return
        
        # 添加用户消息
        self.add_message("用户", message)
        self.message_input.text = ''
        
        # 模拟AI回复
        self.voice_engine.speak("正在思考")
        
        # 调用AI助手获取回复
        reply = self.ai_assistant.get_response(message)
        self.add_message("AI", reply)
        self.voice_engine.speak(reply)
    
    def _generate_reply(self, message):
        """生成AI回复"""
        message = message.lower()
        
        if '天气' in message:
            return "今天天气晴朗，温度适宜，适合外出活动。"
        elif '订餐' in message or '吃饭' in message:
            return "好的，我帮您打开订餐服务。请问您想吃什么？"
        elif '药' in message or '吃药' in message:
            return "请记得按时服药。需要我设置用药提醒吗？"
        elif '紧急' in message or '帮助' in message:
            return "请不要担心，我会立即为您联系紧急联系人。"
        elif '你好' in message or '您好' in message:
            return "您好！很高兴为您服务。请问有什么可以帮助您的？"
        else:
            return "我理解您的问题。让我为您查询一下相关信息。"
    
    def ask_quick_question(self, question):
        """快速提问"""
        self.message_input.text = question
        self.send_message()
    
    def start_voice_input(self):
        """开始语音输入"""
        self.voice_engine.speak("请说话")
        # 启动语音识别
