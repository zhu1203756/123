"""
娱乐中心页面 - 使用统一UI样式
支持有声读物和戏曲播放（集成喜马拉雅API）
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from screens.base_screen import BaseScreen
from styles import get_color, get_font_size, DIMENSIONS
from services.ximalaya_service import get_ximalaya_service
from services.audio_player import get_audio_player
from services.mock_ximalaya_service import get_mock_ximalaya_service


class EntertainmentScreen(BaseScreen):
    name = StringProperty('entertainment')
    
    def __init__(self, voice_engine, entertainment_service, app, **kwargs):
        self.title = '娱乐中心'
        super().__init__(voice_engine, app, **kwargs)
        self.entertainment_service = entertainment_service
        self.ximalaya_service = get_ximalaya_service()
        self.mock_ximalaya_service = get_mock_ximalaya_service()  # 添加模拟服务
        self.audio_player = get_audio_player()
        self.current_content = None
        self.current_content_type = None
        self.is_playing = False
        self.content_list_widget = None
        self.current_albums = []
        self.current_tracks = []
        self.current_track_index = 0
        self.use_mock_data = False  # 是否使用模拟数据
        
        self.build_ui()
    
    def build_ui(self):
        """构建娱乐界面"""
        super().build_ui()
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=15)
        
        # 搜索区域
        search_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.08),
                                  spacing=10)
        
        self.search_input = TextInput(
            hint_text='搜索有声书、戏曲...',
            font_size=get_font_size('body'),
            size_hint=(0.7, 1),
            multiline=False
        )
        
        search_btn = self.create_button(
            text='🔍 搜索',
            color_key='primary',
            size_hint=(0.3, 1),
            on_press=self.on_search
        )
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        content.add_widget(search_layout)
        
        # 类型选择按钮
        type_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.08),
                                spacing=10)
        
        self.audiobook_btn = self._create_type_button('有声读物', 'audiobook')
        self.opera_btn = self._create_type_button('戏曲', 'opera')
        self.hot_btn = self._create_type_button('热门推荐', 'hot')
        
        type_layout.add_widget(self.audiobook_btn)
        type_layout.add_widget(self.opera_btn)
        type_layout.add_widget(self.hot_btn)
        content.add_widget(type_layout)
        
        # 内容显示区域
        content_card = self.create_card(orientation='vertical', size_hint=(1, 0.5),
                                        padding=15, spacing=10)
        
        self.content_title = Label(
            text='请选择有声读物或戏曲',
            font_size=get_font_size('heading'),
            bold=True,
            color=get_color('primary'),
            size_hint=(1, None),
            height=40,
            halign='center'
        )
        self.content_title.bind(size=self.content_title.setter('text_size'))
        content_card.add_widget(self.content_title)
        
        # 内容列表
        content_scroll = ScrollView(size_hint=(1, 1))
        self.content_list_widget = GridLayout(cols=1, size_hint=(1, None),
                                             spacing=8, padding=5)
        self.content_list_widget.bind(minimum_height=self.content_list_widget.setter('height'))
        
        content_scroll.add_widget(self.content_list_widget)
        content_card.add_widget(content_scroll)
        content.add_widget(content_card)
        
        # 播放控制区域
        control_card = self.create_card(orientation='vertical', size_hint=(1, 0.25),
                                        padding=15, spacing=10)
        
        # 当前播放信息
        self.now_playing_label = Label(
            text='当前未播放',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(1, None),
            height=30,
            halign='center'
        )
        self.now_playing_label.bind(size=self.now_playing_label.setter('text_size'))
        control_card.add_widget(self.now_playing_label)
        
        # 播放控制按钮
        control_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1),
                                   spacing=15)
        
        self.prev_btn = self.create_button(
            text='上一首',
            color_key='secondary',
            size_hint=(0.3, 1),
            on_press=self.play_previous
        )
        
        self.play_btn = self.create_button(
            text='播放',
            color_key='success',
            size_hint=(0.4, 1),
            on_press=self.toggle_play
        )
        
        self.next_btn = self.create_button(
            text='下一首',
            color_key='secondary',
            size_hint=(0.3, 1),
            on_press=self.play_next
        )
        
        control_layout.add_widget(self.prev_btn)
        control_layout.add_widget(self.play_btn)
        control_layout.add_widget(self.next_btn)
        control_card.add_widget(control_layout)
        
        content.add_widget(control_card)
        
        # 停止按钮
        stop_btn = self.create_button(
            text='停止播放',
            color_key='danger',
            size_hint=(1, 0.08),
            on_press=self.stop_playback
        )
        content.add_widget(stop_btn)
        
        self.content_area.add_widget(content)
        
        # 默认加载有声读物
        Clock.schedule_once(lambda dt: self.show_audiobooks(), 0.5)
    
    def _create_type_button(self, text, content_type):
        """创建类型选择按钮"""
        btn = Button(
            text=text,
            font_size=get_font_size('button'),
            bold=True,
            background_color=get_color('secondary'),
            color=get_color('text_light')
        )
        btn.bind(on_press=lambda x: self.on_type_select(content_type))
        return btn
    
    def on_type_select(self, content_type):
        """选择内容类型"""
        if content_type == 'audiobook':
            self.show_audiobooks()
        elif content_type == 'opera':
            self.show_opera()
        elif content_type == 'hot':
            self.show_hot_albums()
    
    def on_search(self, instance=None):
        """搜索内容"""
        keyword = self.search_input.text.strip()
        if not keyword:
            if self.voice_engine:
                self.voice_engine.speak('请输入搜索关键词')
            return
        
        self.content_title.text = f'搜索结果: {keyword}'
        if self.voice_engine:
            self.voice_engine.speak(f'正在搜索{keyword}')
        
        # 使用喜马拉雅API搜索
        albums = self.ximalaya_service.search_albums(keyword)
        
        # 如果API失败，使用模拟数据
        if not albums:
            print("API获取失败，使用模拟数据")
            self.use_mock_data = True
            albums = self.mock_ximalaya_service.search_albums(keyword)
        
        self.current_albums = albums
        self.current_content_type = 'album'
        
        if albums:
            self._update_album_list(albums)
        else:
            self.content_list_widget.clear_widgets()
            no_result = Label(
                text='未找到相关内容',
                font_size=get_font_size('body'),
                color=get_color('text_secondary'),
                size_hint=(1, None),
                height=100
            )
            self.content_list_widget.add_widget(no_result)
    
    def show_audiobooks(self):
        """显示有声读物列表"""
        self.content_title.text = '有声读物'
        if self.voice_engine:
            self.voice_engine.speak('正在加载有声读物')
        
        # 使用喜马拉雅API搜索有声书
        albums = self.ximalaya_service.search_albums('有声书', count=20)
        
        # 如果API失败，使用模拟数据
        if not albums:
            print("API获取失败，使用模拟数据")
            self.use_mock_data = True
            albums = self.mock_ximalaya_service.search_albums('有声书', count=20)
        
        self.current_albums = albums
        self.current_content_type = 'album'
        
        if albums:
            self._update_album_list(albums)
        else:
            # 使用模拟数据
            self._show_mock_audiobooks()
    
    def show_opera(self):
        """显示戏曲列表"""
        self.content_title.text = '戏曲列表'
        if self.voice_engine:
            self.voice_engine.speak('正在加载戏曲')
        
        # 使用喜马拉雅API搜索戏曲
        albums = self.ximalaya_service.search_albums('戏曲', count=20)
        
        # 如果API失败，使用模拟数据
        if not albums:
            print("API获取失败，使用模拟数据")
            self.use_mock_data = True
            albums = self.mock_ximalaya_service.search_albums('戏曲', count=20)
        
        self.current_albums = albums
        self.current_content_type = 'album'
        
        if albums:
            self._update_album_list(albums)
        else:
            # 使用模拟数据
            self._show_mock_opera()
    
    def show_hot_albums(self):
        """显示热门推荐"""
        self.content_title.text = '热门推荐'
        if self.voice_engine:
            self.voice_engine.speak('正在加载热门推荐')
        
        # 使用喜马拉雅API获取热门专辑
        albums = self.ximalaya_service.get_hot_albums(count=20)
        
        # 如果API失败，使用模拟数据
        if not albums:
            print("API获取失败，使用模拟数据")
            self.use_mock_data = True
            albums = self.mock_ximalaya_service.get_hot_albums(count=20)
        
        self.current_albums = albums
        self.current_content_type = 'album'
        
        if albums:
            self._update_album_list(albums)
        else:
            self._show_mock_audiobooks()
    
    def _show_mock_audiobooks(self):
        """显示模拟有声书数据"""
        audiobooks = [
            {'title': '红楼梦', 'author': '曹雪芹', 'duration': '120分钟'},
            {'title': '西游记', 'author': '吴承恩', 'duration': '150分钟'},
            {'title': '三国演义', 'author': '罗贯中', 'duration': '180分钟'},
            {'title': '水浒传', 'author': '施耐庵', 'duration': '140分钟'},
            {'title': '围城', 'author': '钱钟书', 'duration': '90分钟'},
            {'title': '骆驼祥子', 'author': '老舍', 'duration': '80分钟'},
        ]
        self._update_content_list(audiobooks, 'audiobook')
    
    def _show_mock_opera(self):
        """显示模拟戏曲数据"""
        operas = [
            {'title': '贵妃醉酒', 'type': '京剧', 'duration': '25分钟'},
            {'title': '霸王别姬', 'type': '京剧', 'duration': '30分钟'},
            {'title': '牡丹亭', 'type': '昆曲', 'duration': '45分钟'},
            {'title': '梁山伯与祝英台', 'type': '越剧', 'duration': '60分钟'},
            {'title': '天仙配', 'type': '黄梅戏', 'duration': '40分钟'},
            {'title': '花木兰', 'type': '豫剧', 'duration': '50分钟'},
        ]
        self._update_content_list(operas, 'opera')
    
    def _update_album_list(self, albums):
        """更新专辑列表"""
        self.content_list_widget.clear_widgets()
        
        for i, album in enumerate(albums):
            # 创建一个水平布局作为行
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=10, padding=8)
            
            # 序号
            index_label = Label(
                text=f'{i + 1}.',
                font_size=get_font_size('body'),
                color=get_color('text_secondary'),
                size_hint=(0.1, 1)
            )
            row.add_widget(index_label)
            
            # 信息
            info_layout = BoxLayout(orientation='vertical', size_hint=(0.6, 1))
            title_label = Label(
                text=album.get('title', ''),
                font_size=get_font_size('body'),
                bold=True,
                color=get_color('text_primary'),
                size_hint=(1, 0.6),
                halign='left'
            )
            title_label.bind(size=title_label.setter('text_size'))
            
            subtitle = f"作者: {album.get('author', '')} · {album.get('track_count', 0)}集"
            
            sub_label = Label(
                text=subtitle,
                font_size=get_font_size('caption'),
                color=get_color('text_secondary'),
                size_hint=(1, 0.4),
                halign='left'
            )
            sub_label.bind(size=sub_label.setter('text_size'))
            
            info_layout.add_widget(title_label)
            info_layout.add_widget(sub_label)
            row.add_widget(info_layout)
            
            # 查看按钮
            def on_view_press(instance, a=album):
                print(f"查看按钮被点击: {a.get('title', '')}")
                self.show_album_tracks(a)
            
            view_btn = Button(
                text='查看',
                font_size=get_font_size('button'),
                bold=True,
                color=get_color('text_light'),
                background_color=get_color('secondary'),
                background_normal='',
                size_hint=(0.15, 1),
                on_press=on_view_press
            )
            row.add_widget(view_btn)
            
            # 播放按钮
            def on_play_press(instance, a=album):
                print(f"播放按钮被点击: {a.get('title', '')}")
                self.play_album_first_track(a)
            
            play_btn = Button(
                text='▶ 播放',
                font_size=get_font_size('button'),
                bold=True,
                color=get_color('text_light'),
                background_color=get_color('primary'),
                background_normal='',
                size_hint=(0.15, 1),
                on_press=on_play_press
            )
            row.add_widget(play_btn)
            
            self.content_list_widget.add_widget(row)
    
    def _create_album_item(self, album, index):
        """创建专辑项"""
        # 创建一个简单的BoxLayout，确保按钮能够正确接收点击事件
        row = BoxLayout(orientation='horizontal', size_hint=(1, None),
                       height=80, spacing=10, padding=8)
        
        # 确保布局能够正确更新
        row.bind(size=lambda instance, value: instance.canvas.ask_update())
        row.bind(pos=lambda instance, value: instance.canvas.ask_update())
        
        # 序号
        index_label = Label(
            text=f'{index + 1}.',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(0.1, 1)
        )
        row.add_widget(index_label)
        
        # 信息
        info_layout = BoxLayout(orientation='vertical', size_hint=(0.6, 1))
        title_label = Label(
            text=album.get('title', ''),
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('text_primary'),
            size_hint=(1, 0.6),
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        subtitle = f"作者: {album.get('author', '')} · {album.get('track_count', 0)}集"
        
        sub_label = Label(
            text=subtitle,
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, 0.4),
            halign='left'
        )
        sub_label.bind(size=sub_label.setter('text_size'))
        
        info_layout.add_widget(title_label)
        info_layout.add_widget(sub_label)
        row.add_widget(info_layout)
        
        # 查看按钮
        def on_view_press(instance):
            print(f"查看按钮被点击: {album.get('title', '')}")
            self.show_album_tracks(album)
        
        view_btn = Button(
            text='查看',
            font_size=get_font_size('button'),
            bold=True,
            color=get_color('text_light'),
            background_color=get_color('secondary'),
            background_normal='',
            size_hint=(0.15, 1),
            on_press=on_view_press
        )
        row.add_widget(view_btn)
        
        # 播放按钮
        def on_play_press(instance):
            print(f"播放按钮被点击: {album.get('title', '')}")
            self.play_album_first_track(album)
        
        play_btn = Button(
            text='▶ 播放',
            font_size=get_font_size('button'),
            bold=True,
            color=get_color('text_light'),
            background_color=get_color('primary'),
            background_normal='',
            size_hint=(0.15, 1),
            on_press=on_play_press
        )
        row.add_widget(play_btn)
        
        return row
    
    def show_album_tracks(self, album):
        """显示专辑下的声音列表"""
        album_id = album.get('id')
        if not album_id:
            return
        
        self.content_title.text = f'{album.get("title", "")} - 声音列表'
        if self.voice_engine:
            self.voice_engine.speak(f'正在加载{album.get("title", "")}')
        
        # 获取专辑下的声音
        tracks = self.ximalaya_service.get_album_tracks(album_id)
        
        # 如果API失败，使用模拟数据
        if not tracks:
            print("API获取失败，使用模拟数据")
            self.use_mock_data = True
            tracks = self.mock_ximalaya_service.get_album_tracks(album_id)
        
        self.current_tracks = tracks
        self.current_content_type = 'track'
        
        if tracks:
            self._update_track_list(tracks)
        else:
            self.content_list_widget.clear_widgets()
            no_result = Label(
                text='该专辑暂无声音',
                font_size=get_font_size('body'),
                color=get_color('text_secondary'),
                size_hint=(1, None),
                height=100
            )
            self.content_list_widget.add_widget(no_result)
    
    def _update_track_list(self, tracks):
        """更新声音列表"""
        self.content_list_widget.clear_widgets()
        
        for i, track in enumerate(tracks):
            track_widget = self._create_track_item(track, i)
            self.content_list_widget.add_widget(track_widget)
    
    def _create_track_item(self, track, index):
        """创建声音项"""
        row = BoxLayout(orientation='horizontal', size_hint=(1, None),
                       height=70, spacing=10, padding=8)
        
        with row.canvas.before:
            Color(*get_color('background'))
            RoundedRectangle(size=row.size, pos=row.pos,
                           radius=[DIMENSIONS['card_radius']])
        
        def update_row(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*get_color('background'))
                RoundedRectangle(size=instance.size, pos=instance.pos,
                               radius=[DIMENSIONS['card_radius']])
        
        row.bind(size=update_row, pos=update_row)
        
        # 序号
        index_label = Label(
            text=f'{index + 1}.',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(0.1, 1)
        )
        row.add_widget(index_label)
        
        # 信息
        info_layout = BoxLayout(orientation='vertical', size_hint=(0.7, 1))
        title_label = Label(
            text=track.get('title', ''),
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('text_primary'),
            size_hint=(1, 0.6),
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        # 时长格式化
        duration = track.get('duration', 0)
        duration_str = f'{duration // 60}:{duration % 60:02d}'
        
        sub_label = Label(
            text=f'时长: {duration_str}',
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, 0.4),
            halign='left'
        )
        sub_label.bind(size=sub_label.setter('text_size'))
        
        info_layout.add_widget(title_label)
        info_layout.add_widget(sub_label)
        row.add_widget(info_layout)
        
        # 播放按钮
        play_btn = self.create_button(
            text='▶ 播放',
            color_key='primary',
            size_hint=(0.2, 1),
            on_press=lambda x, t=track, i=index: self.play_track(t, i)
        )
        row.add_widget(play_btn)
        
        return row
    
    def play_album_first_track(self, album):
        """播放专辑的第一个声音"""
        album_id = album.get('id')
        if not album_id:
            return
        
        # 获取专辑下的声音
        tracks = self.ximalaya_service.get_album_tracks(album_id, count=1)
        
        # 如果API失败，使用模拟数据
        if not tracks:
            print("API获取失败，使用模拟数据")
            self.use_mock_data = True
            tracks = self.mock_ximalaya_service.get_album_tracks(album_id, count=1)
        
        if tracks:
            self.current_tracks = tracks
            self.play_track(tracks[0], 0)
        else:
            if self.voice_engine:
                self.voice_engine.speak('该专辑暂无声音')
    
    def play_track(self, track, index):
        """播放指定声音"""
        print(f"\n{'='*50}")
        print(f"[play_track] 被调用")
        print(f"{'='*50}")
        
        self.current_track_index = index
        
        # 获取声音详情（包含播放URL）
        track_id = track.get('id')
        play_url = track.get('play_url')
        
        print(f"[play_track] 准备播放: {track.get('title', '')}")
        print(f"[play_track] Track ID: {track_id}")
        print(f"[play_track] 原始 Play URL: {play_url}")
        print(f"[play_track] use_mock_data: {self.use_mock_data}")
        
        # 尝试从API获取声音详情
        if track_id and not self.use_mock_data:
            try:
                track_info = self.ximalaya_service.get_track_info(track_id)
                if track_info and track_info.get('play_url'):
                    track = track_info
                    play_url = track_info.get('play_url')
                    print(f"从API获取的播放URL: {play_url}")
            except Exception as e:
                print(f"从API获取声音详情失败: {e}")
        
        # 如果没有播放URL，使用备用音频
        if not play_url:
            print("警告: 没有播放URL，使用备用音频")
            # 使用本地音频文件作为备用
            import os
            backup_audio = os.path.join(os.path.dirname(__file__), '..', 'assets', 'test_audio.wav')
            if os.path.exists(backup_audio):
                play_url = backup_audio
                print(f"使用备用音频: {backup_audio}")
            else:
                # 如果备用音频也不存在，使用Windows系统音效
                windows_sound = 'C:/Windows/Media/notify.wav'
                if os.path.exists(windows_sound):
                    play_url = windows_sound
                    print(f"使用Windows系统音效: {windows_sound}")
                else:
                    play_url = None
                    print("备用音频文件不存在")
        
        # 如果仍然没有播放URL，显示错误提示
        if not play_url:
            self.now_playing_label.text = '无法播放：没有可用的音频源'
            self.now_playing_label.color = get_color('danger')
            if self.voice_engine:
                self.voice_engine.speak('无法播放音频，请检查网络连接')
            return
        
        # 更新track的播放URL
        track['play_url'] = play_url
        print(f"最终播放URL: {play_url}")
        
        # 播放音频
        success = self.audio_player.play(track, on_complete=self.on_track_complete)
        
        if success:
            self.current_content = track
            self.now_playing_label.text = f'正在播放: {track.get("title", "")}'
            self.now_playing_label.color = get_color('success')
            
            if self.voice_engine:
                self.voice_engine.speak(f'正在播放{track.get("title", "")}')
            
            self.is_playing = True
            self.play_btn.text = '⏸ 暂停'
        else:
            self.now_playing_label.text = '播放失败'
            self.now_playing_label.color = get_color('danger')
            if self.voice_engine:
                self.voice_engine.speak('播放失败，请重试')
    
    def on_track_complete(self):
        """声音播放完成回调"""
        # 自动播放下一首
        if self.current_track_index < len(self.current_tracks) - 1:
            next_index = self.current_track_index + 1
            self.play_track(self.current_tracks[next_index], next_index)
        else:
            self.is_playing = False
            self.play_btn.text = '▶ 播放'
            self.now_playing_label.text = '播放完成'
            if self.voice_engine:
                self.voice_engine.speak('播放完成')
    
    def _update_content_list(self, items, item_type):
        """更新内容列表"""
        self.content_list_widget.clear_widgets()
        
        for i, item in enumerate(items):
            item_widget = self._create_content_item(item, item_type, i)
            self.content_list_widget.add_widget(item_widget)
    
    def _create_content_item(self, item, item_type, index):
        """创建内容项"""
        row = BoxLayout(orientation='horizontal', size_hint=(1, None),
                       height=80, spacing=10, padding=8)
        
        with row.canvas.before:
            Color(*get_color('background'))
            RoundedRectangle(size=row.size, pos=row.pos,
                           radius=[DIMENSIONS['card_radius']])
        
        def update_row(instance, value):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(*get_color('background'))
                RoundedRectangle(size=instance.size, pos=instance.pos,
                               radius=[DIMENSIONS['card_radius']])
        
        row.bind(size=update_row, pos=update_row)
        
        # 序号
        index_label = Label(
            text=f'{index + 1}.',
            font_size=get_font_size('body'),
            color=get_color('text_secondary'),
            size_hint=(0.1, 1)
        )
        row.add_widget(index_label)
        
        # 信息
        info_layout = BoxLayout(orientation='vertical', size_hint=(0.6, 1))
        title_label = Label(
            text=item.get('title', ''),
            font_size=get_font_size('body'),
            bold=True,
            color=get_color('text_primary'),
            size_hint=(1, 0.6),
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        # 副标题（作者或类型）
        if item_type == 'audiobook':
            subtitle = f"作者: {item.get('author', '')} · {item.get('duration', '')}"
        else:
            subtitle = f"{item.get('type', '')} · {item.get('duration', '')}"
        
        sub_label = Label(
            text=subtitle,
            font_size=get_font_size('caption'),
            color=get_color('text_secondary'),
            size_hint=(1, 0.4),
            halign='left'
        )
        sub_label.bind(size=sub_label.setter('text_size'))
        
        info_layout.add_widget(title_label)
        info_layout.add_widget(sub_label)
        row.add_widget(info_layout)
        
        # 播放按钮
        play_btn = self.create_button(
            text='▶ 播放',
            color_key='primary',
            size_hint=(0.3, 1),
            on_press=lambda x, i=item: self.select_and_play(i)
        )
        row.add_widget(play_btn)
        
        return row
    
    def select_and_play(self, item):
        """选择并播放内容"""
        self.current_content = item
        self.now_playing_label.text = f'正在播放: {item.get("title", "")}'
        self.now_playing_label.color = get_color('success')
        
        if self.voice_engine:
            self.voice_engine.speak(f'正在播放{item.get("title", "")}')
        
        # 调用服务播放
        if self.entertainment_service:
            self.entertainment_service.play_content(self.current_content_type, item.get('title', ''))
        
        self.is_playing = True
        self.play_btn.text = '⏸ 暂停'
    
    def toggle_play(self, instance=None):
        """播放/暂停切换"""
        if not self.current_content:
            if self.voice_engine:
                self.voice_engine.speak('请先选择要播放的内容')
            return
        
        if self.is_playing:
            # 暂停播放
            self.audio_player.pause()
            self.is_playing = False
            self.play_btn.text = '▶ 播放'
            self.now_playing_label.text = f'已暂停: {self.current_content.get("title", "")}'
            if self.voice_engine:
                self.voice_engine.speak('暂停播放')
        else:
            # 恢复播放
            self.audio_player.resume()
            self.is_playing = True
            self.play_btn.text = '⏸ 暂停'
            self.now_playing_label.text = f'正在播放: {self.current_content.get("title", "")}'
            if self.voice_engine:
                self.voice_engine.speak('继续播放')
    
    def play_previous(self, instance=None):
        """上一首"""
        if not self.current_tracks or self.current_track_index <= 0:
            if self.voice_engine:
                self.voice_engine.speak('已经是第一首了')
            return
        
        prev_index = self.current_track_index - 1
        self.play_track(self.current_tracks[prev_index], prev_index)
        if self.voice_engine:
            self.voice_engine.speak('上一首')
    
    def play_next(self, instance=None):
        """下一首"""
        if not self.current_tracks or self.current_track_index >= len(self.current_tracks) - 1:
            if self.voice_engine:
                self.voice_engine.speak('已经是最后一首了')
            return
        
        next_index = self.current_track_index + 1
        self.play_track(self.current_tracks[next_index], next_index)
        if self.voice_engine:
            self.voice_engine.speak('下一首')
    
    def stop_playback(self, instance=None):
        """停止播放"""
        self.audio_player.stop()
        self.is_playing = False
        self.current_content = None
        self.play_btn.text = '▶ 播放'
        self.now_playing_label.text = '当前未播放'
        self.now_playing_label.color = get_color('text_secondary')
        
        if self.voice_engine:
            self.voice_engine.speak('停止播放')
