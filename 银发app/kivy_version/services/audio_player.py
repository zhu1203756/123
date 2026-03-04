"""
音频播放器服务
支持播放网络音频流
"""
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from typing import Callable, Optional


class AudioPlayer:
    """音频播放器类"""
    
    def __init__(self):
        self.sound = None
        self.current_track = None
        self.is_playing = False
        self.on_progress_callback = None
        self.on_complete_callback = None
        self.progress_event = None
    
    def play(self, track_info: dict, on_complete: Callable = None) -> bool:
        """播放音频"""
        try:
            print(f"[AudioPlayer] 开始播放流程")
            
            # 停止当前播放
            print(f"[AudioPlayer] 停止当前播放")
            self.stop()
            
            # 获取播放URL
            play_url = track_info.get('play_url')
            print(f"[AudioPlayer] 播放URL: {play_url}")
            
            if not play_url:
                print("[AudioPlayer] 错误: 没有播放URL")
                return False
            
            # 检查文件是否存在
            import os
            if not os.path.exists(play_url):
                print(f"[AudioPlayer] 错误: 音频文件不存在: {play_url}")
                return False
            
            print(f"[AudioPlayer] 正在加载音频...")
            # 加载音频
            self.sound = SoundLoader.load(play_url)
            
            if not self.sound:
                print(f"[AudioPlayer] 错误: 无法加载音频: {play_url}")
                return False
            
            print(f"[AudioPlayer] 音频加载成功，时长: {self.sound.length}秒")
            
            self.current_track = track_info
            self.on_complete_callback = on_complete
            
            # 绑定完成事件
            self.sound.bind(on_stop=self._on_sound_stop)
            
            # 播放
            print(f"[AudioPlayer] 开始播放...")
            self.sound.play()
            self.is_playing = True
            
            # 启动进度更新
            self.progress_event = Clock.schedule_interval(self._update_progress, 0.5)
            
            print(f"[AudioPlayer] 播放成功: {track_info.get('title', '未知')}")
            return True
            
        except Exception as e:
            print(f"[AudioPlayer] 播放音频失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def pause(self):
        """暂停播放"""
        if self.sound and self.is_playing:
            self.sound.stop()
            self.is_playing = False
            if self.progress_event:
                self.progress_event.cancel()
    
    def resume(self):
        """恢复播放"""
        if self.sound and not self.is_playing:
            self.sound.play()
            self.is_playing = True
            self.progress_event = Clock.schedule_interval(self._update_progress, 0.5)
    
    def stop(self):
        """停止播放"""
        if self.sound:
            self.sound.stop()
            self.sound.unbind(on_stop=self._on_sound_stop)
            self.sound = None
        
        self.is_playing = False
        self.current_track = None
        
        if self.progress_event:
            self.progress_event.cancel()
            self.progress_event = None
    
    def seek(self, position: float):
        """跳转到指定位置（秒）"""
        if self.sound:
            self.sound.seek(position)
    
    def get_position(self) -> float:
        """获取当前播放位置（秒）"""
        if self.sound:
            return self.sound.get_pos()
        return 0.0
    
    def get_duration(self) -> float:
        """获取音频总时长（秒）"""
        if self.sound:
            return self.sound.length
        return 0.0
    
    def set_volume(self, volume: float):
        """设置音量 (0.0 - 1.0)"""
        if self.sound:
            self.sound.volume = max(0.0, min(1.0, volume))
    
    def get_volume(self) -> float:
        """获取当前音量"""
        if self.sound:
            return self.sound.volume
        return 1.0
    
    def _update_progress(self, dt):
        """更新播放进度"""
        if self.on_progress_callback and self.sound:
            position = self.get_position()
            duration = self.get_duration()
            if duration > 0:
                progress = position / duration
                self.on_progress_callback(position, duration, progress)
    
    def _on_sound_stop(self, instance):
        """音频播放完成回调"""
        self.is_playing = False
        if self.progress_event:
            self.progress_event.cancel()
            self.progress_event = None
        
        if self.on_complete_callback:
            self.on_complete_callback()
    
    def is_current_track(self, track_id) -> bool:
        """检查是否正在播放指定曲目"""
        if self.current_track:
            return self.current_track.get('id') == track_id
        return False


# 单例模式
_audio_player = None


def get_audio_player() -> AudioPlayer:
    """获取音频播放器单例"""
    global _audio_player
    if _audio_player is None:
        _audio_player = AudioPlayer()
    return _audio_player
