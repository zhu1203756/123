import requests
import json
from typing import Dict, List, Optional
from kivy.utils import platform

class EmergencyService:
    def __init__(self):
        self.emergency_numbers = {
            "120": "120",
            "110": "110",
            "119": "119"
        }
    
    def call_emergency(self, contact_type: str, phone_number: str, location: Optional[Dict] = None):
        message = f"正在呼叫{contact_type}：{phone_number}"
        if location:
            message += f"\n位置信息：{location.get('address', '未知地址')}"
        
        # 尝试在手机上实际呼叫
        try:
            if platform == 'android':
                # 使用Pyjnius调用Android的Intent系统
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                # 创建拨号Intent
                intent = Intent(Intent.ACTION_DIAL)
                intent.setData(Uri.parse(f"tel:{phone_number}"))
                
                # 启动Intent
                current_activity = PythonActivity.mActivity
                current_activity.startActivity(intent)
                
                message = f"已启动呼叫{contact_type}：{phone_number}"
            elif platform == 'ios':
                # 使用Pyobjus调用iOS的API
                # 注意：需要安装pyobjus库
                try:
                    from pyobjus import autoclass
                    UIApplication = autoclass('UIApplication')
                    NSURL = autoclass('NSURL')
                    
                    # 创建URL并打开
                    url = NSURL.URLWithString_(f"tel:{phone_number}")
                    UIApplication.sharedApplication().openURL_(url)
                    
                    message = f"已启动呼叫{contact_type}：{phone_number}"
                except Exception as e:
                    print(f"iOS呼叫失败: {e}")
            else:
                # 非移动平台，模拟呼叫
                print(f"[紧急呼叫] {message}")
        except Exception as e:
            print(f"呼叫失败: {e}")
        
        return message
    
    def send_emergency_sms(self, phone_number: str, message: str, location: Optional[Dict] = None):
        full_message = message
        if location:
            full_message += f"\n位置：{location.get('address', '未知地址')}"
        
        print(f"模拟发送紧急短信到 {phone_number}: {full_message}")
        return f"已发送紧急短信到 {phone_number}"

    
    def get_current_location(self) -> Dict:
        """使用腾讯地图SDK获取当前位置"""
        try:
            # 腾讯地图IP定位API
            # 注意：这里需要替换为真实的腾讯地图API密钥
            # 申请地址：https://lbs.qq.com/dev/console/application/mine
            api_key = "BJMBZ-N5ALJ-LFYF2-XIPXN-AGPCQ-NEB36"  # 示例密钥，需要替换
            url = f"https://apis.map.qq.com/ws/location/v1/ip?key={api_key}"
            
            print(f"正在请求腾讯地图IP定位API: {url}")
            response = requests.get(url, timeout=5)
            print(f"API响应状态码: {response.status_code}")
            print(f"API响应内容: {response.text}")
            
            data = response.json()
            print(f"解析后的API响应: {data}")
            
            if data.get('status') == 0:
                result = data.get('result', {})
                location = result.get('location', {})
                address = result.get('address', '未知地址')
                
                print(f"IP定位返回: 地址={address}, 纬度={location.get('lat')}, 经度={location.get('lng')}")
                
                # 检查address_component字段
                address_component = result.get('address_component', {})
                print(f"address_component: {address_component}")
                
                if address == '未知地址':
                    # 尝试从address_component构建地址
                    if address_component:
                        province = address_component.get('province', '')
                        city = address_component.get('city', '')
                        district = address_component.get('district', '')
                        street = address_component.get('street', '')
                        street_number = address_component.get('street_number', '')
                        
                        print(f"地址组件: 省={province}, 市={city}, 区={district}, 街道={street}, 门牌号={street_number}")
                        
                        # 构建详细地址
                        address_parts = [province, city, district, street, street_number]
                        address = ''.join(filter(None, address_parts))
                        
                        print(f"从address_component构建的地址: {address}")
                    
                    # 如果仍然没有地址信息，使用逆地理编码API获取详细地址
                    if not address or address == '未知地址':
                        lat = location.get('lat', 0)
                        lng = location.get('lng', 0)
                        if lat and lng:
                            # 腾讯地图逆地理编码API
                            reverse_url = f"https://apis.map.qq.com/ws/geocoder/v1/?location={lat},{lng}&key={api_key}"
                            print(f"正在请求逆地理编码API: {reverse_url}")
                            
                            reverse_response = requests.get(reverse_url, timeout=5)
                            reverse_data = reverse_response.json()
                            print(f"逆地理编码API响应: {reverse_data}")
                            
                            if reverse_data.get('status') == 0:
                                reverse_result = reverse_data.get('result', {})
                                print(f"逆地理编码result: {reverse_result}")
                                
                                # 尝试获取formatted_address
                                formatted_address = reverse_result.get('formatted_address', '')
                                print(f"formatted_address: {formatted_address}")
                                
                                # 如果没有formatted_address，尝试获取address_component
                                if not formatted_address:
                                    address_component = reverse_result.get('address_component', {})
                                    print(f"逆地理编码address_component: {address_component}")
                                    if address_component:
                                        province = address_component.get('province', '')
                                        city = address_component.get('city', '')
                                        district = address_component.get('district', '')
                                        street = address_component.get('street', '')
                                        street_number = address_component.get('street_number', '')
                                        
                                        address_parts = [province, city, district, street, street_number]
                                        formatted_address = ''.join(filter(None, address_parts))
                                        print(f"从逆地理编码address_component构建的地址: {formatted_address}")
                                
                                if formatted_address:
                                    address = formatted_address
                                    print(f"逆地理编码获取的地址: {address}")
                    
                    # 如果仍然没有地址信息，使用经纬度作为地址
                    if not address or address == '未知地址':
                        lat = location.get('lat', 0)
                        lng = location.get('lng', 0)
                        address = f"位置坐标: {lat:.6f}, {lng:.6f}"
                        print(f"使用经纬度作为地址: {address}")
                
                print(f"最终获取的位置: {address}, 纬度: {location.get('lat')}, 经度: {location.get('lng')}")
                
                return {
                    "latitude": location.get('lat', 39.9042),
                    "longitude": location.get('lng', 116.4074),
                    "address": address
                }
            else:
                # API调用失败，返回默认位置
                error_message = data.get('message', '未知错误')
                print(f"API调用失败: {error_message}")
                return {
                    "latitude": 39.9042,
                    "longitude": 116.4074,
                    "address": f"北京市朝阳区 (API错误: {error_message})"
                }
        except Exception as e:
            print(f"获取位置失败: {e}")
            # 异常情况下返回默认位置
            return {
                "latitude": 39.9042,
                "longitude": 116.4074,
                "address": f"北京市朝阳区 (网络错误: {str(e)[:20]})"
            }

class PaymentService:
    def __init__(self, voice_engine=None, db_manager=None):
        self.voice_engine = voice_engine
        self.db_manager = db_manager
        self.payment_types = {
            "water": "水费",
            "electricity": "电费",
            "gas": "燃气费",
            "property": "物业费",
            "phone": "话费"
        }
    
    def get_payment_amount(self, payment_type: str, account_number: str) -> float:
        amounts = {
            "water": 45.5,
            "electricity": 120.0,
            "gas": 68.5,
            "property": 200.0,
            "phone": 50.0
        }
        return amounts.get(payment_type, 0.0)
    
    def process_payment(self, payment_type: str, account_number: str, amount: float) -> Dict:
        print(f"处理支付：{self.payment_types.get(payment_type, payment_type)} - {amount}元")
        return {
            "success": True,
            "message": f"{self.payment_types.get(payment_type, payment_type)}支付成功，金额：{amount}元",
            "transaction_id": f"TXN{hash(account_number) % 1000000}"
        }
    
    def get_payment_history(self, account_number: str) -> List[Dict]:
        return [
            {"type": "电费", "amount": 120.0, "date": "2024-01-15", "status": "已完成"},
            {"type": "水费", "amount": 45.5, "date": "2024-01-10", "status": "已完成"},
            {"type": "话费", "amount": 50.0, "date": "2024-01-05", "status": "已完成"}
        ]

class CommunityService:
    def __init__(self, voice_engine=None, db_manager=None):
        self.voice_engine = voice_engine
        self.db_manager = db_manager
    
    def get_notifications(self, notification_type: Optional[str] = None) -> List[Dict]:
        """从数据库获取社区通知"""
        try:
            from database import get_db_connection, close_db_connection
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                # 查询所有激活的通知
                cursor.execute('SELECT id, title, content, created_at FROM notices WHERE is_active=1 ORDER BY created_at DESC')
                notifications = []
                
                for row in cursor.fetchall():
                    notifications.append({
                        "id": row[0],
                        "title": row[1],
                        "content": row[2],
                        "type": "community",  # 默认类型
                        "date": row[3].split(' ')[0]  # 只取日期部分
                    })
                
                close_db_connection(conn)
                return notifications
        except Exception as e:
            print(f"获取社区通知失败: {e}")
        
        # 如果数据库获取失败，返回默认通知
        return [
            {
                "id": 1,
                "title": "社区体检通知",
                "content": "本周六上午9点在社区服务中心开展免费体检活动，欢迎参加。",
                "type": "health",
                "date": "2024-01-20"
            },
            {
                "id": 2,
                "title": "老年大学招生",
                "content": "社区老年大学春季班开始招生，开设书法、绘画、舞蹈等课程。",
                "type": "activity",
                "date": "2024-01-18"
            },
            {
                "id": 3,
                "title": "疫苗接种提醒",
                "content": "请符合条件的老年人及时接种流感疫苗。",
                "type": "health",
                "date": "2024-01-15"
            }
        ]
    
    def get_activities(self) -> List[Dict]:
        return [
            {"name": "太极拳晨练", "time": "每天早上7点", "location": "社区广场"},
            {"name": "书法班", "time": "每周二、四下午2点", "location": "活动室"},
            {"name": "广场舞", "time": "每天晚上7点", "location": "社区广场"},
            {"name": "健康讲座", "time": "每月第一周周六", "location": "社区会议室"}
        ]
    
    def call_emergency(self, contact_type: str, phone_number: str, location: Optional[Dict] = None):
        """模拟紧急呼叫"""
        message = f"正在呼叫{contact_type}：{phone_number}"
        if location:
            message += f"\n位置信息：{location.get('address', '未知地址')}"
        print(f"[紧急呼叫] {message}")
        return message
    
    def send_emergency_sms(self, phone_number: str, message: str, location: Optional[Dict] = None):
        """模拟发送紧急短信"""
        full_message = message
        if location:
            full_message += f"\n位置：{location.get('address', '未知地址')}"
        
        print(f"[紧急短信] 发送到 {phone_number}: {full_message}")
        return f"已发送紧急短信到 {phone_number}"

class MealService:
    def __init__(self, voice_engine=None, db_manager=None):
        self.voice_engine = voice_engine
        self.db_manager = db_manager
    
    def get_menu(self) -> List[Dict]:
        """从数据库获取菜品信息"""
        try:
            from database import get_db_connection, close_db_connection
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                
                # 查询所有可用的菜品
                cursor.execute('SELECT id, name, price, description FROM dishes WHERE is_available=1')
                menu_items = []
                
                for row in cursor.fetchall():
                    menu_items.append({
                        "id": row[0],
                        "name": row[1],
                        "price": row[2],
                        "description": row[3]
                    })
                
                close_db_connection(conn)
                return menu_items
        except Exception as e:
            print(f"获取菜品信息失败: {e}")
        
        # 如果数据库获取失败，返回默认菜品
        return [
            {"name": "红烧肉套餐", "price": 25.0, "description": "红烧肉+米饭+青菜"},
            {"name": "清蒸鱼套餐", "price": 28.0, "description": "清蒸鱼+米饭+时蔬"},
            {"name": "豆腐套餐", "price": 18.0, "description": "家常豆腐+米饭+汤"},
            {"name": "营养粥", "price": 8.0, "description": "小米粥/南瓜粥"},
            {"name": "包子套餐", "price": 12.0, "description": "肉包+菜包+豆浆"}
        ]
    
    def place_order(self, items: List[Dict], address: str, phone: str) -> Dict:
        total = sum(item["price"] for item in items)
        return {
            "success": True,
            "order_id": f"ORD{hash(address) % 1000000}",
            "total": total,
            "estimated_time": "30分钟",
            "message": f"订单已提交，预计{30}分钟送达"
        }

class EntertainmentService:
    def __init__(self, voice_engine=None):
        self.voice_engine = voice_engine
        # 喜马拉雅API配置
        self.xmly_app_key = "your_app_key"  # 替换为实际的App Key
        self.xmly_app_secret = "your_app_secret"  # 替换为实际的App Secret
        self.xmly_api_url = "https://api.ximalaya.com"
        
        # 有声读物数据
        self.audiobooks = [
            {"title": "红楼梦", "author": "曹雪芹", "duration": "120分钟", "id": "1"},
            {"title": "三国演义", "author": "罗贯中", "duration": "150分钟", "id": "2"},
            {"title": "西游记", "author": "吴承恩", "duration": "140分钟", "id": "3"},
            {"title": "水浒传", "author": "施耐庵", "duration": "130分钟", "id": "4"},
            {"title": "围城", "author": "钱钟书", "duration": "90分钟", "id": "5"},
            {"title": "骆驼祥子", "author": "老舍", "duration": "80分钟", "id": "6"},
            {"title": "茶馆", "author": "老舍", "duration": "70分钟", "id": "7"},
            {"title": "四世同堂", "author": "老舍", "duration": "160分钟", "id": "8"},
            {"title": "平凡的世界", "author": "路遥", "duration": "180分钟", "id": "9"},
            {"title": "活着", "author": "余华", "duration": "85分钟", "id": "10"},
        ]
        
        # 戏曲数据
        self.opera = [
            {"title": "贵妃醉酒", "type": "京剧", "duration": "25分钟", "id": "101"},
            {"title": "霸王别姬", "type": "京剧", "duration": "30分钟", "id": "102"},
            {"title": "空城计", "type": "京剧", "duration": "20分钟", "id": "103"},
            {"title": "牡丹亭", "type": "昆曲", "duration": "45分钟", "id": "104"},
            {"title": "长生殿", "type": "昆曲", "duration": "40分钟", "id": "105"},
            {"title": "梁山伯与祝英台", "type": "越剧", "duration": "60分钟", "id": "106"},
            {"title": "天仙配", "type": "黄梅戏", "duration": "35分钟", "id": "107"},
            {"title": "女驸马", "type": "黄梅戏", "duration": "38分钟", "id": "108"},
            {"title": "花木兰", "type": "豫剧", "duration": "50分钟", "id": "109"},
            {"title": "穆桂英挂帅", "type": "豫剧", "duration": "42分钟", "id": "110"},
            {"title": "白蛇传", "type": "川剧", "duration": "55分钟", "id": "111"},
            {"title": "秦香莲", "type": "评剧", "duration": "48分钟", "id": "112"},
        ]
        
        # 音频播放状态
        self.is_playing = False
        self.current_audio = None
    
    def get_audiobooks(self) -> List[Dict]:
        # 尝试从喜马拉雅API获取有声读物
        try:
            # 这里是喜马拉雅API调用示例
            # 实际使用时需要替换为真实的API调用
            # url = f"{self.xmly_api_url}/v2/search"
            # params = {
            #     "q": "有声读物",
            #     "app_key": self.xmly_app_key,
            #     "page": 1,
            #     "count": 10
            # }
            # response = requests.get(url, params=params)
            # data = response.json()
            # 处理API响应数据
            
            # 暂时返回模拟数据
            return self.audiobooks
        except Exception as e:
            print(f"获取有声读物失败: {e}")
            return self.audiobooks
    
    def get_opera(self) -> List[Dict]:
        # 尝试从喜马拉雅API获取戏曲
        try:
            # 这里是喜马拉雅API调用示例
            # 实际使用时需要替换为真实的API调用
            # url = f"{self.xmly_api_url}/v2/search"
            # params = {
            #     "q": "戏曲",
            #     "app_key": self.xmly_app_key,
            #     "page": 1,
            #     "count": 10
            # }
            # response = requests.get(url, params=params)
            # data = response.json()
            # 处理API响应数据
            
            # 暂时返回模拟数据
            return self.opera
        except Exception as e:
            print(f"获取戏曲失败: {e}")
            return self.opera
    
    def play_content(self, content_type: str, title: str) -> str:
        try:
            # 从喜马拉雅API获取音频播放链接
            # 这里是API调用示例
            # content_id = None
            # if content_type == "audiobook":
            #     for book in self.audiobooks:
            #         if book["title"] == title:
            #             content_id = book["id"]
            #             break
            # else:
            #     for item in self.opera:
            #         if item["title"] == title:
            #             content_id = item["id"]
            #             break
            # 
            # if content_id:
            #     url = f"{self.xmly_api_url}/v2/tracks"
            #     params = {
            #         "id": content_id,
            #         "app_key": self.xmly_app_key
            #     }
            #     response = requests.get(url, params=params)
            #     data = response.json()
            #     处理播放链接
            
            # 模拟播放
            self.is_playing = True
            self.current_audio = title
            
            # 播放提示音
            if platform == 'android':
                # Android平台使用TTS
                if self.voice_engine:
                    self.voice_engine.speak(f"正在播放：{title}")
            else:
                # 桌面平台使用winsound
                import winsound
                winsound.Beep(800, 500)
                winsound.Beep(1000, 500)
            
            return f"正在播放：{title}"
        except Exception as e:
            print(f"播放失败: {e}")
            return f"播放失败：{str(e)}"
    
    def stop_content(self) -> str:
        if self.is_playing:
            self.is_playing = False
            self.current_audio = None
            return "已停止播放"
        return "当前没有播放内容"
