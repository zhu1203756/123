"""
喜马拉雅API服务 - 在线听书功能
使用H5接入方式调用喜马拉雅API
"""
import requests
import hashlib
import time
from typing import Dict, List, Optional


class XimalayaService:
    """喜马拉雅API服务类"""
    
    def __init__(self, app_key: str = "55f51ce58efa2d86d116ff9b17a8b664", app_secret: str = "5d358a4bd146feb5d473d974c4ab6e78"):
        self.app_key = app_key
        self.app_secret = app_secret
        self.base_url = "https://api.ximalaya.com"
        self.session = requests.Session()
        # 使用Android_ID_MD5格式的device_id
        import hashlib
        android_id = "867425031234567"
        self.device_id = hashlib.md5(android_id.encode()).hexdigest()
        self.device_sn = self.device_id
        import random
        self.random = random
        
    def _generate_sign(self, params: Dict) -> str:
        """生成API签名"""
        # 按参数名排序并拼接
        sorted_params = sorted(params.items())
        param_str = ''.join([f"{k}{v}" for k, v in sorted_params])
        # 添加app_secret
        sign_str = param_str + self.app_secret
        # MD5加密
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    def search_albums(self, keyword: str, page: int = 1, count: int = 20) -> List[Dict]:
        """搜索专辑"""
        try:
            nonce = str(self.random.randint(100000, 999999))
            params = {
                'app_key': self.app_key,
                'keyword': keyword,
                'page': page,
                'count': count,
                'client_os_type': 3,  # Web平台
                'device_id': self.device_id,
                'device_id_type': 'Android_ID_MD5',
                'device_sn': self.device_sn,
                'server_api_version': '1.0',
                'ts': int(time.time()),
                'nonce': nonce
            }
            params['sign'] = self._generate_sign(params)
            
            response = self.session.get(
                f"{self.base_url}/search/albums",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ret') == 0:
                    albums = data.get('albums', [])
                    return [{
                        'id': album.get('id'),
                        'title': album.get('title'),
                        'cover': album.get('cover_url'),
                        'author': album.get('nickname'),
                        'play_count': album.get('play_count', 0),
                        'track_count': album.get('tracks_count', 0)
                    } for album in albums]
            
            print(f"搜索专辑失败: {response.status_code}")
            return []
            
        except Exception as e:
            print(f"搜索专辑异常: {e}")
            return []
    
    def get_album_tracks(self, album_id: int, page: int = 1, count: int = 20) -> List[Dict]:
        """获取专辑下的声音列表"""
        try:
            params = {
                'app_key': self.app_key,
                'album_id': album_id,
                'page': page,
                'count': count,
                'client_os_type': 3,  # Web平台
                'device_id': self.device_id,
                'device_sn': self.device_sn,
                'ts': int(time.time())
            }
            params['sign'] = self._generate_sign(params)
            
            response = self.session.get(
                f"{self.base_url}/v2/albums/browse",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ret') == 0:
                    tracks = data.get('tracks', [])
                    return [{
                        'id': track.get('id'),
                        'title': track.get('title'),
                        'duration': track.get('duration', 0),
                        'play_url': track.get('play_url_32') or track.get('play_url_64'),
                        'cover': track.get('cover_url'),
                        'create_time': track.get('created_at')
                    } for track in tracks]
            
            print(f"获取专辑声音失败: {response.status_code}")
            return []
            
        except Exception as e:
            print(f"获取专辑声音异常: {e}")
            return []
    
    def get_track_info(self, track_id: int) -> Optional[Dict]:
        """获取声音详情"""
        try:
            params = {
                'app_key': self.app_key,
                'track_id': track_id,
                'client_os_type': 3,  # Web平台
                'device_id': self.device_id,
                'device_sn': self.device_sn,
                'ts': int(time.time())
            }
            params['sign'] = self._generate_sign(params)
            
            response = self.session.get(
                f"{self.base_url}/v2/tracks/get",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ret') == 0:
                    track = data.get('track', {})
                    return {
                        'id': track.get('id'),
                        'title': track.get('title'),
                        'duration': track.get('duration', 0),
                        'play_url': track.get('play_url_32') or track.get('play_url_64'),
                        'cover': track.get('cover_url'),
                        'album_title': track.get('album_title'),
                        'author': track.get('nickname')
                    }
            
            print(f"获取声音详情失败: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"获取声音详情异常: {e}")
            return None
    
    def get_hot_albums(self, category_id: int = 1, page: int = 1, count: int = 20) -> List[Dict]:
        """获取热门专辑"""
        try:
            params = {
                'app_key': self.app_key,
                'category_id': category_id,
                'page': page,
                'count': count,
                'client_os_type': 3,  # Web平台
                'device_id': self.device_id,
                'device_sn': self.device_sn,
                'ts': int(time.time())
            }
            params['sign'] = self._generate_sign(params)
            
            response = self.session.get(
                f"{self.base_url}/v2/albums/hot",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ret') == 0:
                    albums = data.get('albums', [])
                    return [{
                        'id': album.get('id'),
                        'title': album.get('title'),
                        'cover': album.get('cover_url'),
                        'author': album.get('nickname'),
                        'play_count': album.get('play_count', 0),
                        'track_count': album.get('tracks_count', 0)
                    } for album in albums]
            
            print(f"获取热门专辑失败: {response.status_code}")
            return []
            
        except Exception as e:
            print(f"获取热门专辑异常: {e}")
            return []
    
    def get_categories(self) -> List[Dict]:
        """获取分类列表"""
        try:
            params = {
                'app_key': self.app_key,
                'ts': int(time.time())
            }
            params['sign'] = self._generate_sign(params)
            
            response = self.session.get(
                f"{self.base_url}/v2/categories/list",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ret') == 0:
                    categories = data.get('categories', [])
                    return [{
                        'id': cat.get('id'),
                        'name': cat.get('name'),
                        'cover': cat.get('cover_url')
                    } for cat in categories]
            
            print(f"获取分类列表失败: {response.status_code}")
            return []
            
        except Exception as e:
            print(f"获取分类列表异常: {e}")
            return []


# 单例模式
_ximalaya_service = None


def get_ximalaya_service() -> XimalayaService:
    """获取喜马拉雅服务单例"""
    global _ximalaya_service
    if _ximalaya_service is None:
        _ximalaya_service = XimalayaService()
    return _ximalaya_service
