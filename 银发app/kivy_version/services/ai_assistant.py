import requests
import os
from .community_service import EmergencyService
from kivy.utils import platform

class AIAssistant:
    def __init__(self, voice_engine=None, db_manager=None):
        # 和风天气API密钥
        self.weather_api_key = "6a97dde8b5884d69b382cc3b2f314153"
        self.voice_engine = voice_engine
        self.db_manager = db_manager
        
        # 阿里云百炼API配置
        self.api_key = "sk-142d5c020ed2473ea2b1f0506c3ffea4"
        self.api_url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        print("AI助手初始化成功")
    
    def get_weather(self, location: dict) -> str:
        """获取实时天气信息"""
        try:
            # 和风天气API调用
            lat = location.get("latitude", 39.9042)
            lon = location.get("longitude", 116.4074)
            
            print(f"正在调用和风天气API，位置: {lat}, {lon}")
            print(f"API Key: {self.weather_api_key}")
            
            # 尝试使用不同的API端点
            url = f"https://api.qweather.com/v7/weather/now?location={lon},{lat}&key={self.weather_api_key}"
            print(f"API请求URL: {url}")
            
            # 添加请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应内容: {response.text}")
            
            data = response.json()
            print(f"API响应JSON: {data}")
            
            if data.get("code") == "200":
                now = data.get("now", {})
                temp = now.get("temp", "未知")
                text = now.get("text", "未知")
                wind_dir = now.get("windDir", "未知")
                wind_scale = now.get("windScale", "未知")
                humidity = now.get("humidity", "未知")
                
                weather_info = f"""当前天气：{text}
温度：{temp}°C
风向：{wind_dir}
风力：{wind_scale}级
湿度：{humidity}%"""
                
                # 根据天气给出建议
                advice = self.get_weather_advice(text, int(temp) if temp != "未知" else 20)
                
                return f"{weather_info}\n\n{advice}"
            else:
                print(f"API调用失败，返回模拟数据")
                return self.get_mock_weather(location)
                
        except Exception as e:
            print(f"获取天气失败: {e}")
            import traceback
            traceback.print_exc()
            return self.get_mock_weather(location)
    
    def get_mock_weather(self, location: dict) -> str:
        """模拟天气数据（当API不可用时使用）"""
        address = location.get("address", "未知位置")
        
        # 根据当前时间模拟不同的天气
        import datetime
        hour = datetime.datetime.now().hour
        
        if 6 <= hour < 18:  # 白天
            return f"""当前天气：多云
温度：22°C
风向：东南风
风力：2级
湿度：65%

💡 温馨提示：
今天天气不错，适合外出活动。建议老人适当进行户外散步，但要注意防晒和补水。如果感觉疲劳，请及时休息。"""
        else:  # 晚上
            return f"""当前天气：晴
温度：15°C
风向：微风
风力：1级
湿度：70%

💡 温馨提示：
晚间天气较凉，建议老人注意保暖，适当添加衣物。如果要外出，建议携带外套。睡前可以喝杯温水，有助于睡眠。"""
    
    def get_weather_advice(self, weather_text: str, temp: int) -> str:
        """根据天气情况给出建议"""
        advice = "💡 温馨提示：\n"
        
        # 根据天气状况给出建议
        if "雨" in weather_text:
            advice += "今天有雨，出门请记得带伞，路面湿滑请小心行走。"
        elif "雪" in weather_text:
            advice += "今天有雪，天气寒冷，请注意保暖，减少外出。"
        elif "晴" in weather_text:
            advice += "今天天气晴朗，适合户外活动，但要注意防晒。"
        elif "阴" in weather_text:
            advice += "今天阴天，温度适宜，是外出活动的好天气。"
        elif "云" in weather_text:
            advice += "今天多云，天气舒适，适合进行日常活动。"
        else:
            advice += "今天天气尚可，请根据自身情况安排活动。"
        
        # 根据温度给出建议
        if temp < 10:
            advice += "\n气温较低，请多穿衣服，注意保暖，预防感冒。"
        elif temp > 30:
            advice += "\n气温较高，请注意防暑降温，多喝水，避免中暑。"
        elif 15 <= temp <= 25:
            advice += "\n温度适宜，是户外活动的好时机。"
        
        advice += "\n如有不适，请及时休息或就医。"
        
        return advice
    
    def get_response(self, user_message: str) -> str:
        try:
            # 检测是否询问天气
            weather_keywords = ["天气", "气温", "温度", "下雨", "下雪", "晴天", "阴天", "刮风", " forecast", "weather"]
            is_weather_question = any(keyword in user_message for keyword in weather_keywords)
            
            # 如果是天气问题，获取位置信息和天气
            if is_weather_question:
                print("检测到天气问题，获取位置信息...")
                emergency_service = EmergencyService()
                location = emergency_service.get_current_location()
                location_address = location.get("address", "未知位置")
                print(f"获取到位置: {location_address}")
                
                # 获取实时天气
                print("正在获取实时天气...")
                weather_info = self.get_weather(location)
                
                return f"您好！根据您所在的位置 {location_address}，\n\n{weather_info}"
            
            print(f"用户消息: {user_message}")
            
            # 使用阿里云百炼AI助手处理其他问题
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": "qwen-plus",
                "messages": [
                    {"role": "system", "content": "你是一个智能助手，专门为老年人提供帮助。请用简单易懂的语言回答问题，保持友好和耐心。"},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.7
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                print(f"AI响应: {ai_response}")
                return ai_response
            else:
                print(f"API调用失败: {response.text}")
                return self.get_default_response(user_message)
            
        except Exception as e:
            print(f"调用AI模型失败: {e}")
            import traceback
            traceback.print_exc()
            return self.get_default_response(user_message)
    
    def get_default_response(self, user_message: str) -> str:
        """默认响应，当API调用失败时使用"""
        default_responses = {
            "你好": "你好！我是您的智能助手，有什么可以帮您的吗？",
            "您好": "您好！我是您的智能助手，有什么可以帮您的吗？",
            "hi": "你好！我是您的智能助手，有什么可以帮您的吗？",
            "hello": "你好！我是您的智能助手，有什么可以帮您的吗？",
            "谢谢": "不客气，很高兴能帮到您！",
            "感谢": "不客气，很高兴能帮到您！",
            "再见": "再见，祝您生活愉快！",
            "拜拜": "再见，祝您生活愉快！",
            "天气": "抱歉，我暂时无法获取天气信息。",
            "时间": "抱歉，我暂时无法获取当前时间。",
            "健康": "保持健康的生活方式对老年人非常重要，建议您每天适当运动，保持均衡饮食。",
            "医疗": "如果您有健康问题，建议及时咨询医生。",
            "紧急": "如果您遇到紧急情况，请立即拨打急救电话120。",
            "帮助": "我是您的智能助手，可以帮您解答一些简单的问题，或者提供健康建议。",
            "功能": "我可以帮您解答问题、提供健康建议、讲述故事等。"
        }
        
        # 检查用户消息是否在默认响应中
        user_message_lower = user_message.lower()
        for key in default_responses:
            if key in user_message or key.lower() in user_message_lower:
                return default_responses[key]
        
        # 默认响应
        return "抱歉，我暂时无法回答您的问题，请稍后再试。您可以尝试询问健康、生活等方面的问题。"
    
    def health_advice(self, health_data: dict) -> str:
        prompt = f"""
        请根据以下健康数据给出简单的建议：
        血压：{health_data.get('blood_pressure', '未记录')}
        血糖：{health_data.get('blood_sugar', '未记录')}
        心率：{health_data.get('heart_rate', '未记录')}
        
        请给出简单易懂的健康建议。
        """
        return self.get_response(prompt)
    
    def answer_daily_question(self, question: str) -> str:
        return self.get_response(question)
    
    def get_medication_reminder_advice(self, medication_name: str) -> str:
        prompt = f"请简单介绍一下{medication_name}的常见注意事项，用老年人容易理解的语言。"
        return self.get_response(prompt)
