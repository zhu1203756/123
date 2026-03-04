import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ========== 字体配置（必须在导入任何Kivy模块之前）==========
# 尝试使用系统自带的中文字体
font_paths = [
    'C:/Windows/Fonts/simhei.ttf',  # 黑体
    'C:/Windows/Fonts/simsun.ttc',  # 宋体
    'C:/Windows/Fonts/microsoftyahei.ttf',  # 微软雅黑
    'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑 (另一种文件名)
    'C:/Windows/Fonts/msyhbd.ttc',  # 微软雅黑粗体
]

chinese_font_path = None
for font_path in font_paths:
    if os.path.exists(font_path):
        chinese_font_path = font_path
        break

if chinese_font_path:
    print(f"成功加载中文字体: {chinese_font_path}")
else:
    print("警告：未找到中文字体，将使用默认字体")
# =========================================================

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.config import Config
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

# 设置窗口大小（模拟手机屏幕）
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')

# 注册中文字体
if chinese_font_path:
    LabelBase.register(name='ChineseFont', fn_regular=chinese_font_path)
    # 设置Kivy默认字体
    Config.set('kivy', 'default_font', 'ChineseFont')
    
    # 使用KV语言设置默认字体和样式
    Builder.load_string('''
<Label>:
    font_name: 'ChineseFont'
    
<Button>:
    font_name: 'ChineseFont'
    
<TextInput>:
    font_name: 'ChineseFont'
    font_size: 16
    
<Spinner>:
    font_name: 'ChineseFont'
    background_normal: ''
    background_down: ''
    background_color: 0.97, 0.98, 1.0, 1
    color: 0.25, 0.3, 0.4, 1
    
<SpinnerOption>:
    font_name: 'ChineseFont'
    background_normal: ''
    background_down: ''
    background_color: 0.97, 0.98, 1.0, 1
    color: 0.25, 0.3, 0.4, 1
    canvas.before:
        Color: 
            rgba: 0.97, 0.98, 1.0, 1
        Rectangle:
            size: self.size
            pos: self.pos
''')
    print("已设置KV默认字体")

from voice.voice_engine import VoiceEngine
from services.ai_assistant import AIAssistant
from services.community_service import CommunityService, MealService, PaymentService, EntertainmentService, EmergencyService
from models.database import DatabaseManager
from utils.message_manager import message_manager


class SilverHairApp(App):
    def build(self):
        Window.title = "银发关爱"
        
        # 初始化数据库
        from database import init_database
        init_database()
        
        # 初始化服务
        self.db_manager = DatabaseManager()
        self.voice_engine = VoiceEngine()
        self.ai_assistant = AIAssistant(self.voice_engine, self.db_manager)
        self.community_service = CommunityService(self.voice_engine, self.db_manager)
        self.meal_service = MealService(self.voice_engine, self.db_manager)
        self.payment_service = PaymentService(self.voice_engine, self.db_manager)
        self.entertainment_service = EntertainmentService(self.voice_engine)
        
        # 创建屏幕管理器
        self.screen_manager = ScreenManager()
        
        # 导入并添加所有屏幕
        from screens.main_screen import MainScreen
        from screens.meal_screen import MealScreen
        from screens.payment_screen import PaymentScreen
        from screens.health_screen import HealthScreen
        from screens.health_detail_screen import HealthDetailScreen
        from screens.entertainment_screen import EntertainmentScreen
        from screens.notification_screen import NotificationScreen
        from screens.ai_assistant_screen import AIAssistantScreen
        from screens.emergency_screen import EmergencyScreen
        from screens.admin_screen import AdminLoginScreen, AdminRegisterScreen, AdminMainScreen, DishPublishScreen, NoticePublishScreen
        from screens.voice_settings_screen import VoiceSettingsScreen
        from screens.calculator_screen import CalculatorScreen
        
        # 创建屏幕实例
        self.main_screen = MainScreen(
            voice_engine=self.voice_engine,
            ai_assistant=self.ai_assistant,
            community_service=self.community_service,
            meal_service=self.meal_service,
            payment_service=self.payment_service,
            entertainment_service=self.entertainment_service,
            db_manager=self.db_manager,
            app=self
        )
        
        self.meal_screen = MealScreen(
            voice_engine=self.voice_engine,
            meal_service=self.meal_service,
            db_manager=self.db_manager,
            app=self
        )
        
        self.payment_screen = PaymentScreen(
            voice_engine=self.voice_engine,
            payment_service=self.payment_service,
            db_manager=self.db_manager,
            app=self
        )
        
        self.health_screen = HealthScreen(
            voice_engine=self.voice_engine,
            db_manager=self.db_manager,
            app=self
        )
        
        self.health_detail_screen = HealthDetailScreen(
            voice_engine=self.voice_engine,
            db_manager=self.db_manager,
            app=self
        )
        
        self.entertainment_screen = EntertainmentScreen(
            voice_engine=self.voice_engine,
            entertainment_service=self.entertainment_service,
            app=self
        )
        
        self.notification_screen = NotificationScreen(
            voice_engine=self.voice_engine,
            community_service=self.community_service,
            db_manager=self.db_manager,
            app=self
        )
        
        self.ai_assistant_screen = AIAssistantScreen(
            voice_engine=self.voice_engine,
            ai_assistant=self.ai_assistant,
            app=self
        )
        
        self.emergency_screen = EmergencyScreen(
            voice_engine=self.voice_engine,
            community_service=self.community_service,
            db_manager=self.db_manager,
            app=self
        )
        
        self.admin_login_screen = AdminLoginScreen()
        self.admin_register_screen = AdminRegisterScreen()
        self.admin_main_screen = AdminMainScreen()
        self.dish_publish_screen = DishPublishScreen()
        self.notice_publish_screen = NoticePublishScreen()
        
        self.voice_settings_screen = VoiceSettingsScreen(
            voice_engine=self.voice_engine,
            app=self
        )
        
        self.calculator_screen = CalculatorScreen(
            voice_engine=self.voice_engine,
            app=self
        )
        
        # 添加所有屏幕
        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.meal_screen)
        self.screen_manager.add_widget(self.payment_screen)
        self.screen_manager.add_widget(self.health_screen)
        self.screen_manager.add_widget(self.health_detail_screen)
        self.screen_manager.add_widget(self.entertainment_screen)
        self.screen_manager.add_widget(self.notification_screen)
        self.screen_manager.add_widget(self.ai_assistant_screen)
        self.screen_manager.add_widget(self.emergency_screen)
        self.screen_manager.add_widget(self.admin_login_screen)
        self.screen_manager.add_widget(self.admin_register_screen)
        self.screen_manager.add_widget(self.admin_main_screen)
        self.screen_manager.add_widget(self.dish_publish_screen)
        self.screen_manager.add_widget(self.notice_publish_screen)
        self.screen_manager.add_widget(self.voice_settings_screen)
        self.screen_manager.add_widget(self.calculator_screen)
        
        # 默认显示主屏幕
        self.screen_manager.current = 'main'
        
        return self.screen_manager
    
    def show_screen(self, screen_name):
        """切换到指定屏幕"""
        self.screen_manager.current = screen_name
    
    def on_stop(self):
        """应用关闭时的清理工作"""
        if hasattr(self, 'voice_engine') and hasattr(self.voice_engine, 'stop'):
            try:
                self.voice_engine.stop()
            except:
                pass


if __name__ == '__main__':
    SilverHairApp().run()
