from kivy.utils import platform

# 根据平台选择语音引擎
if platform == 'android':
    from .mobile_voice_engine import MobileVoiceEngine as VoiceEngine
else:
    # 尝试导入原项目的语音引擎
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from 银发app.voice.voice_engine import VoiceEngine
    except ImportError:
        # 如果原项目的语音引擎不可用，使用移动语音引擎的桌面版本
        from .mobile_voice_engine import MobileVoiceEngine as VoiceEngine
