import time
import winsound

class AudioBookLogic:
    def __init__(self):
        self.current_audio = None
        self.is_playing = False
        # 模拟数据
        self.audio_books = [
            "三国演义",
            "西游记",
            "水浒传",
            "红楼梦",
            "聊斋志异"
        ]
        self.operas = [
            "京剧：霸王别姬",
            "豫剧：花木兰",
            "越剧：梁山伯与祝英台",
            "黄梅戏：天仙配",
            "评剧：杨三姐告状"
        ]
    
    def get_audio_books(self):
        """获取有声读物列表"""
        return self.audio_books
    
    def get_operas(self):
        """获取戏曲列表"""
        return self.operas
    
    def play_audio(self, audio_name):
        """播放音频"""
        self.current_audio = audio_name
        self.is_playing = True
        print(f"正在播放：{audio_name}")
        
        # 尝试播放音频
        try:
            # 使用系统蜂鸣音播放
            print("播放提示音...")
            winsound.Beep(800, 500)  # 800Hz，500ms
            time.sleep(0.5)
            winsound.Beep(1000, 500)  # 1000Hz，500ms
            print("音频播放完成")
            
        except Exception as e:
            print(f"播放音频失败：{str(e)}")
            # 如果播放失败，仍然标记为正在播放（模拟）
            pass
        
        return True
    
    def stop_audio(self):
        """停止播放"""
        if self.is_playing:
            print(f"停止播放：{self.current_audio}")
            self.is_playing = False
            self.current_audio = None
            return True
        return False
    
    def is_audio_playing(self):
        """检查是否正在播放"""
        return self.is_playing
    
    def get_current_audio(self):
        """获取当前播放的音频"""
        return self.current_audio
