"""
字体配置模块 - 为Kivy应用提供中文字体支持
必须在导入任何Kivy UI组件之前调用
"""
import os

def setup_fonts():
    """设置中文字体为Kivy默认字体"""
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
        # 导入Kivy配置
        from kivy.config import Config
        from kivy.core.text import LabelBase
        
        # 注册中文字体
        LabelBase.register(name='ChineseFont', fn_regular=chinese_font_path)
        
        # 设置Kivy默认字体（必须在创建任何UI组件之前）
        Config.set('kivy', 'default_font', ['ChineseFont', chinese_font_path])
        
        print(f"成功加载中文字体: {chinese_font_path}")
        return True
    else:
        print("警告：未找到中文字体，将使用默认字体")
        return False

# 获取字体名称的辅助函数
def get_chinese_font():
    """返回中文字体名称，如果未找到则返回None"""
    font_paths = [
        'C:/Windows/Fonts/simhei.ttf',
        'C:/Windows/Fonts/simsun.ttc',
        'C:/Windows/Fonts/microsoftyahei.ttf',
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/msyhbd.ttc',
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            return 'ChineseFont'
    return None
