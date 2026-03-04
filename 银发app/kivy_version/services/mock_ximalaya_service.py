"""
模拟喜马拉雅数据服务
用于测试和演示
"""
from typing import Dict, List


class MockXimalayaService:
    """模拟喜马拉雅API服务类"""
    
    def __init__(self, app_key: str = "55f51ce58efa2d86d116ff9b17a8b664"):
        self.app_key = app_key
        self.base_url = "https://api.ximalaya.com"
        
        # 模拟数据
        self.mock_albums = [
            {
                'id': 1,
                'title': '三国演义',
                'cover': '',
                'author': '单田芳',
                'play_count': 1000000,
                'track_count': 100
            },
            {
                'id': 2,
                'title': '西游记',
                'cover': '',
                'author': '袁阔成',
                'play_count': 800000,
                'track_count': 80
            },
            {
                'id': 3,
                'title': '水浒传',
                'cover': '',
                'author': '田连元',
                'play_count': 600000,
                'track_count': 60
            },
            {
                'id': 4,
                'title': '红楼梦',
                'cover': '',
                'author': '刘兰芳',
                'play_count': 500000,
                'track_count': 50
            },
            {
                'id': 5,
                'title': '封神演义',
                'cover': '',
                'author': '单田芳',
                'play_count': 400000,
                'track_count': 40
            }
        ]
        
        self.mock_tracks = [
            {
                'id': 1,
                'title': '第一回：桃园三结义',
                'duration': 1800,
                'play_url': None,
                'cover': '',
                'create_time': '2025-01-01'
            },
            {
                'id': 2,
                'title': '第二回：温酒斩华雄',
                'duration': 1700,
                'play_url': None,
                'cover': '',
                'create_time': '2025-01-02'
            },
            {
                'id': 3,
                'title': '第三回：三英战吕布',
                'duration': 1900,
                'play_url': None,
                'cover': '',
                'create_time': '2025-01-03'
            },
            {
                'id': 4,
                'title': '第四回：连环计',
                'duration': 1600,
                'play_url': None,
                'cover': '',
                'create_time': '2025-01-04'
            },
            {
                'id': 5,
                'title': '第五回：白门楼',
                'duration': 1750,
                'play_url': None,
                'cover': '',
                'create_time': '2025-01-05'
            }
        ]
    
    def search_albums(self, keyword: str, page: int = 1, count: int = 20) -> List[Dict]:
        """搜索专辑"""
        print(f"模拟搜索专辑: {keyword}")
        
        # 简单的关键词匹配
        if keyword:
            results = [album for album in self.mock_albums 
                      if keyword.lower() in album['title'].lower()]
        else:
            results = self.mock_albums
        
        return results[:count]
    
    def get_album_tracks(self, album_id: int, page: int = 1, count: int = 20) -> List[Dict]:
        """获取专辑下的声音列表"""
        print(f"模拟获取专辑声音: album_id={album_id}")
        
        # 为每个专辑生成不同的声音
        tracks = []
        for i, track in enumerate(self.mock_tracks):
            track_copy = track.copy()
            track_copy['id'] = album_id * 100 + i
            track_copy['title'] = f"{track['title']} (专辑{album_id})"
            tracks.append(track_copy)
        
        return tracks[:count]
    
    def get_track_info(self, track_id: int) -> Dict:
        """获取声音详情"""
        print(f"模拟获取声音详情: track_id={track_id}")
        
        # 根据track_id返回对应的声音信息
        track_index = track_id % len(self.mock_tracks)
        track = self.mock_tracks[track_index].copy()
        track['id'] = track_id
        track['album_title'] = f'专辑{track_id // 100}'
        track['author'] = '单田芳'
        
        return track
    
    def get_hot_albums(self, category_id: int = 1, page: int = 1, count: int = 20) -> List[Dict]:
        """获取热门专辑"""
        print(f"模拟获取热门专辑: category_id={category_id}")
        
        # 根据分类返回不同的专辑
        albums = []
        for i, album in enumerate(self.mock_albums):
            album_copy = album.copy()
            album_copy['id'] = category_id * 100 + i
            album_copy['title'] = f"{album['title']} (分类{category_id})"
            albums.append(album_copy)
        
        return albums[:count]
    
    def get_categories(self) -> List[Dict]:
        """获取分类列表"""
        return [
            {'id': 1, 'name': '有声读物', 'cover': ''},
            {'id': 2, 'name': '戏曲', 'cover': ''},
            {'id': 3, 'name': '评书', 'cover': ''},
            {'id': 4, 'name': '相声', 'cover': ''}
        ]


# 单例模式
_mock_ximalaya_service = None


def get_mock_ximalaya_service() -> MockXimalayaService:
    """获取模拟喜马拉雅服务单例"""
    global _mock_ximalaya_service
    if _mock_ximalaya_service is None:
        _mock_ximalaya_service = MockXimalayaService()
    return _mock_ximalaya_service
