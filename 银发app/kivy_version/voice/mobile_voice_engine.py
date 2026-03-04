import threading
import queue
import requests
import json
from typing import Callable, Optional
from kivy.utils import platform

class MobileVoiceEngine:
    def __init__(self):
        self.recognizer = None
        self.tts_engine = None
        self.is_listening = False
        self.speech_queue = queue.Queue()
        # 默认声音参数
        self.rate = 150  # 语速
        self.volume = 1.0  # 音量（0.0-1.0）
        self.pitch = 1.0  # 音调（0.5-2.0）
        # 通义千问API配置
        self.tongyi_app_id = "3169359"
        self.tongyi_api_key = "l4nDcTlNZxj6e8dihcFyBMYJ"
        self.tongyi_api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        self._setup_tts()
        
    def _setup_tts(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                # 使用Android的TTS API
                self.tts_engine = autoclass('android.speech.tts.TextToSpeech')
                self.context = autoclass('org.kivy.android.PythonActivity').mActivity
                self.tts = self.tts_engine(self.context, None)
                self.tts.setLanguage(autoclass('java.util.Locale').CHINESE)
            except Exception as e:
                print(f"Android TTS初始化失败: {e}")
                self.tts = None
        else:
            # 桌面平台使用pyttsx3
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', self.rate)
                self.tts_engine.setProperty('volume', self.volume)
            except Exception as e:
                print(f"语音引擎初始化失败: {e}")
                self.tts_engine = None
    
    def set_voice_parameters(self, rate=None, volume=None, pitch=None):
        """设置语音参数"""
        if rate is not None:
            self.rate = rate
            if platform == 'android' and self.tts:
                self.tts.setSpeechRate(rate / 100.0)
            elif self.tts_engine:
                self.tts_engine.setProperty('rate', rate)
        
        if volume is not None:
            self.volume = volume
            if platform == 'android' and self.tts:
                self.tts.setVolume(volume)
            elif self.tts_engine:
                self.tts_engine.setProperty('volume', volume)
        
        if pitch is not None:
            self.pitch = pitch
            # 注意：Android TTS可能不直接支持pitch
    
    def set_voice(self, voice_id=None):
        """设置语音类型"""
        if platform == 'android' and self.tts:
            # Android TTS的语音选择
            pass  # 暂时不实现
        elif self.tts_engine:
            if voice_id is not None:
                self.tts_engine.setProperty('voice', voice_id)
            else:
                # 切换到下一个可用语音
                voices = self.tts_engine.getProperty('voices')
                if voices:
                    current_voice = self.tts_engine.getProperty('voice')
                    current_index = 0
                    for i, voice in enumerate(voices):
                        if voice.id == current_voice:
                            current_index = i
                            break
                    next_index = (current_index + 1) % len(voices)
                    self.tts_engine.setProperty('voice', voices[next_index].id)
                    return voices[next_index].name
        return None
    
    def get_available_voices(self):
        """获取可用的语音列表"""
        if platform == 'android':
            # Android TTS的语音列表
            return [
                ("chinese_female", "中文女声"),
                ("chinese_male", "中文男声"),
                ("chinese_elderly", "中文老年声")
            ]
        elif self.tts_engine:
            voices = self.tts_engine.getProperty('voices')
            voice_list = [(voice.id, voice.name) for voice in voices]
            # 如果只有一个英文语音，添加一些模拟的中文语音选项
            if len(voice_list) <= 1:
                # 添加模拟的中文语音选项
                voice_list.extend([
                    ("chinese_female", "中文女声"),
                    ("chinese_male", "中文男声"),
                    ("chinese_elderly", "中文老年声")
                ])
            return voice_list
        return []
    
    def speak(self, text: str, callback: Optional[Callable] = None):
        def _speak():
            try:
                if platform == 'android' and self.tts:
                    self.tts.speak(text)
                elif self.tts_engine:
                    # 为每个speak调用创建新的引擎实例，避免事件循环冲突
                    try:
                        # 尝试使用当前引擎
                        self.tts_engine.say(text)
                        self.tts_engine.runAndWait()
                    except Exception as e:
                        print(f"当前引擎失败，创建新引擎: {e}")
                        # 创建新的引擎实例
                        import pyttsx3
                        temp_engine = pyttsx3.init()
                        temp_engine.setProperty('rate', self.rate)
                        temp_engine.setProperty('volume', self.volume)
                        if hasattr(self.tts_engine, 'getProperty'):
                            current_voice = self.tts_engine.getProperty('voice')
                            temp_engine.setProperty('voice', current_voice)
                        temp_engine.say(text)
                        temp_engine.runAndWait()
                else:
                    print(f"语音播报(文本): {text}")
                if callback:
                    callback()
            except Exception as e:
                print(f"语音播报错误: {e}")
                print(f"语音播报(文本): {text}")
        
        thread = threading.Thread(target=_speak)
        thread.daemon = True
        thread.start()
    
    def listen(self, timeout: int = 5, language: str = "zh-CN") -> Optional[str]:
        try:
            if platform == 'android':
                # 使用Android的语音识别API
                from jnius import autoclass, cast
                Intent = autoclass('android.content.Intent')
                RecognizerIntent = autoclass('android.speech.RecognizerIntent')
                Activity = autoclass('org.kivy.android.PythonActivity')
                context = Activity.mActivity
                
                intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, language)
                intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
                
                # 这里需要使用ActivityResultLauncher，暂时返回模拟数据
                print("Android语音识别功能需要ActivityResultLauncher实现")
                return None
            else:
                # 桌面平台使用speech_recognition
                import speech_recognition as sr
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source, duration=1)
                    print("正在聆听...")
                    audio = r.listen(source, timeout=timeout)
                
                try:
                    text = r.recognize_google(audio, language=language)
                    print(f"识别结果: {text}")
                    return text
                except sr.UnknownValueError:
                    print("无法识别语音")
                    return None
                except sr.RequestError as e:
                    print(f"语音识别服务错误: {e}")
                    return None
        except Exception as e:
            print(f"录音错误: {e}")
            return None
    
    def start_continuous_listening(self, callback: Callable[[str], None]):
        def _listen_loop():
            self.is_listening = True
            while self.is_listening:
                text = self.listen(timeout=3)
                if text:
                    callback(text)
        
        thread = threading.Thread(target=_listen_loop)
        thread.daemon = True
        thread.start()
    
    def stop_listening(self):
        self.is_listening = False
    
    def speak_menu(self, menu_items: list[str]):
        menu_text = "。".join([f"{i+1}、{item}" for i, item in enumerate(menu_items)])
        self.speak(f"菜单选项：{menu_text}")
    
    def speak_notification(self, title: str, content: str):
        self.speak(f"新通知：{title}。{content}")
    
    def speak_health_data(self, record_type: str, value: float, unit: str):
        self.speak(f"您的{record_type}是{value}{unit}")
    
    def get_ai_response(self, user_input: str, system_prompt: str = "你是一个智能语音助手，专为老年人设计，回答要简洁明了，语气亲切。") -> str:
        """调用通义千问API获取AI回复"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.tongyi_api_key}"
            }
            
            payload = {
                "model": "qwen-turbo",  # 通义千问模型
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7,
                "max_tokens": 512
            }
            
            response = requests.post(self.tongyi_api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            return "抱歉，我现在无法回答您的问题。"
        except Exception as e:
            print(f"AI回复错误: {e}")
            return "抱歉，我现在无法回答您的问题。"
    
    def stop(self):
        """停止语音引擎"""
        self.stop_listening()
        if platform == 'android' and hasattr(self, 'tts') and self.tts:
            try:
                self.tts.stop()
            except Exception as e:
                print(f"停止Android TTS失败: {e}")
        elif self.tts_engine:
            try:
                # 尝试停止pyttsx3引擎
                pass  # pyttsx3没有直接的stop方法
            except Exception as e:
                print(f"停止语音引擎失败: {e}")
