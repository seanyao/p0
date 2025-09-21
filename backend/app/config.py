import json
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """配置管理类，从JSON文件加载配置"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # 默认配置文件路径
            config_path = Path(__file__).parent.parent / "config.json"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_amap_config(self) -> Dict[str, str]:
        """获取高德地图配置"""
        return {
            'api_key': self.get('amap.api_key'),
            'security_key': self.get('amap.security_key'),
            'base_url': self.get('amap.base_url')
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """获取应用配置"""
        return {
            'title': self.get('app.title'),
            'version': self.get('app.version'),
            'debug': self.get('app.debug'),
            'host': self.get('app.host'),
            'port': self.get('app.port')
        }
    
    def get_limits(self) -> Dict[str, int]:
        """获取限制配置"""
        return {
            'min_locations': self.get('limits.min_locations'),
            'max_locations': self.get('limits.max_locations'),
            'daily_api_calls': self.get('limits.daily_api_calls')
        }

# 全局配置实例
config = Config()