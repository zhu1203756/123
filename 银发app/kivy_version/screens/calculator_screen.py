from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from styles import get_color, get_font_size, DIMENSIONS


class CalculatorButton(Button):
    """计算器按钮"""
    def __init__(self, text='', bg_color=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.bg_color = bg_color or get_color('primary')
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        
        # 如果是占位按钮
        if text == '':
            self.disabled = True
            self.opacity = 0
            return
        
        self.font_size = get_font_size('large')
        self.bold = True
        # 根据背景色选择文字颜色
        if bg_color == get_color('card'):
            # 白色背景用深色文字
            self.color = get_color('text_primary')
        else:
            # 彩色背景用白色文字
            self.color = get_color('text_light')
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        # 如果是占位按钮，不绘制背景
        if self.text == '':
            return
        with self.canvas.before:
            Color(*self.bg_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[DIMENSIONS['button_radius']])


class CalculatorScreen(Screen):
    name = StringProperty('calculator')
    
    def __init__(self, voice_engine, app, **kwargs):
        super().__init__(**kwargs)
        self.voice_engine = voice_engine
        self.app = app
        self.current_input = '0'
        self.previous_input = ''
        self.operation = None
        self.should_reset_input = False
        self.full_expression = '0'  # 完整表达式
        
        self.build_ui()
    
    def build_ui(self):
        """构建计算器界面"""
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        with main_layout.canvas.before:
            Color(*get_color('background'))
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self.update_bg, pos=self.update_bg)
        
        # 标题栏
        header = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), padding=[10, 5])
        with header.canvas.before:
            Color(*get_color('info'))
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
            text='计算器',
            size_hint=(0.6, 1),
            font_size=get_font_size('title'),
            bold=True,
            color=get_color('text_light')
        )
        
        header.add_widget(back_btn)
        header.add_widget(title_label)
        header.add_widget(Label(size_hint=(0.2, 1)))
        
        main_layout.add_widget(header)
        
        # 显示屏
        display_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2), padding=[15, 10])
        with display_layout.canvas.before:
            Color(*get_color('card'))
            self.display_rect = RoundedRectangle(size=display_layout.size, pos=display_layout.pos, radius=[DIMENSIONS['card_radius']])
        display_layout.bind(size=self.update_display, pos=self.update_display)
        
        self.display_label = Label(
            text='0',
            font_size=get_font_size('display'),
            color=get_color('text_primary'),
            halign='right',
            valign='middle',
            text_size=(None, None)
        )
        self.display_label.bind(size=self.update_text_size)
        
        display_layout.add_widget(self.display_label)
        main_layout.add_widget(display_layout)
        
        # 按钮区域 - 使用4列布局
        buttons_layout = GridLayout(cols=4, spacing=8, padding=12, size_hint=(1, 0.7))
        
        # 按钮配置 - 按照新布局排列
        buttons = [
            ('C', get_color('danger'), self.clear),        # 第一行：C（红色）
            ('←', get_color('card'), self.backspace),      # 第一行：←（白色）
            ('%', get_color('card'), self.percentage),     # 第一行：%（白色）
            ('÷', get_color('secondary'), self.set_operation),  # 第一行：/（青色）
            ('7', get_color('card'), self.input_number),   # 第二行：7
            ('8', get_color('card'), self.input_number),   # 第二行：8
            ('9', get_color('card'), self.input_number),   # 第二行：9
            ('×', get_color('secondary'), self.set_operation),  # 第二行：*（青色）
            ('4', get_color('card'), self.input_number),   # 第三行：4
            ('5', get_color('card'), self.input_number),   # 第三行：5
            ('6', get_color('card'), self.input_number),   # 第三行：6
            ('-', get_color('secondary'), self.set_operation),  # 第三行：-（青色）
            ('1', get_color('card'), self.input_number),   # 第四行：1
            ('2', get_color('card'), self.input_number),   # 第四行：2
            ('3', get_color('card'), self.input_number),   # 第四行：3
            ('+', get_color('secondary'), self.set_operation),  # 第四行：+（青色）
            ('0', get_color('card'), self.input_number),   # 第五行：0
            ('.', get_color('card'), self.input_decimal),   # 第五行：.
            ('=', get_color('secondary'), self.calculate),  # 第五行：=（青色）
            ('', get_color('background'), lambda x: None),  # 占位
        ]

        # 添加按钮到布局
        for i, (text, bg_color, callback) in enumerate(buttons):
            # 创建按钮
            btn = CalculatorButton(
                text=text,
                bg_color=bg_color,
                size_hint=(1, None),
                height=90  # 按钮高度
            )
            
            # 绑定事件
            btn.bind(on_press=lambda instance, cb=callback, t=text: cb(t))
            
            # 添加到布局
            buttons_layout.add_widget(btn)
        
        main_layout.add_widget(buttons_layout)
        
        self.add_widget(main_layout)
    
    def update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    def update_header(self, instance, value):
        self.header_rect.size = instance.size
        self.header_rect.pos = instance.pos
    
    def update_display(self, instance, value):
        self.display_rect.size = instance.size
        self.display_rect.pos = instance.pos
    
    def update_text_size(self, instance, value):
        instance.text_size = (instance.width - 20, instance.height)
    
    def on_button_press(self, text, callback):
        """按钮按下处理"""
        callback(text)
        if self.voice_engine:
            self.voice_engine.speak(text)
    
    def input_number(self, num):
        """输入数字"""
        if self.should_reset_input:
            self.current_input = num
            # 只有当表达式以 '=' 结尾时才重置 full_expression
            if self.full_expression.endswith('=') or '=' in self.full_expression:
                self.full_expression = num
            else:
                self.full_expression += num
            self.should_reset_input = False
        else:
            if self.current_input == '0':
                self.current_input = num
                if self.full_expression == '0' or self.full_expression.endswith('=0'):
                    self.full_expression = num
                else:
                    self.full_expression += num
            else:
                self.current_input += num
                self.full_expression += num
        self.update_display_text()
    
    def input_decimal(self, _):
        """输入小数点"""
        if self.should_reset_input:
            self.current_input = '0.'
            self.full_expression = '0.'
            self.should_reset_input = False
        elif '.' not in self.current_input:
            self.current_input += '.'
            self.full_expression += '.'
        self.update_display_text()
    
    def clear(self, _):
        """清除"""
        self.current_input = '0'
        self.previous_input = ''
        self.operation = None
        self.should_reset_input = False
        self.full_expression = '0'
        self.update_display_text()
    
    def backspace(self, _):
        """退格"""
        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
            if len(self.full_expression) > 1:
                self.full_expression = self.full_expression[:-1]
            else:
                self.full_expression = '0'
        else:
            self.current_input = '0'
            self.full_expression = '0'
        self.update_display_text()
    
    def set_operation(self, op):
        """设置运算符"""
        if self.operation and not self.should_reset_input:
            self.calculate(None)
        
        self.previous_input = self.current_input
        self.operation = op
        self.full_expression += op
        self.should_reset_input = True
        self.update_display_text()  # 立即更新显示
    
    def calculate(self, _):
        """计算结果"""
        if not self.operation or not self.previous_input:
            return
        
        try:
            prev = float(self.previous_input)
            current = float(self.current_input)
            
            if self.operation == '+':
                result = prev + current
            elif self.operation == '-':
                result = prev - current
            elif self.operation == '×':
                result = prev * current
            elif self.operation == '÷':
                if current == 0:
                    self.current_input = '错误'
                    self.full_expression = '错误'
                    self.update_display_text()
                    return
                result = prev / current
            else:
                return
            
            # 格式化结果
            if result == int(result):
                self.current_input = str(int(result))
            else:
                self.current_input = str(round(result, 8)).rstrip('0').rstrip('.')
            
            # 更新完整表达式
            self.full_expression = f"{self.full_expression}={self.current_input}"
            
            self.operation = None
            self.previous_input = ''
            self.should_reset_input = True
            self.update_display_text()
            
            # 语音播报结果
            if self.voice_engine:
                self.voice_engine.speak(f"结果是{self.current_input}")
                
        except Exception as e:
            self.current_input = '错误'
            self.full_expression = '错误'
            self.update_display_text()
    
    def percentage(self, _):
        """百分比"""
        try:
            value = float(self.current_input)
            result = value / 100
            if result == int(result):
                self.current_input = str(int(result))
            else:
                self.current_input = str(result)
            self.full_expression = f"{self.full_expression}%={self.current_input}"
            self.update_display_text()
        except:
            pass
    
    def update_display_text(self):
        """更新显示文本"""
        self.display_label.text = self.full_expression
    
    def go_back(self, instance):
        """返回主界面"""
        self.app.screen_manager.current = 'main'
