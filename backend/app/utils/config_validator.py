"""
配置文件验证工具
提供配置文件的验证、加载和错误处理功能
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class ConfigValidator:
    """配置文件验证器"""
    
    # 必需的配置字段
    REQUIRED_FIELDS = {
        'llm': ['api_key', 'api_url', 'model'],
        'route_planning': ['max_locations'],
        'geo_service': ['provider']
    }
    
    # 字段类型验证
    FIELD_TYPES = {
        'llm.api_key': str,
        'llm.api_url': str,
        'llm.model': str,
        'llm.max_tokens': int,
        'llm.temperature': (int, float),
        'llm.timeout': int,
        'route_planning.max_locations': int,
        'route_planning.default_style': str,
        'geo_service.provider': str,
        'geo_service.cache_enabled': bool,
        'geo_service.cache_ttl': int
    }
    
    # 字段值范围验证
    FIELD_RANGES = {
        'llm.max_tokens': (1, 10000),
        'llm.temperature': (0.0, 2.0),
        'llm.timeout': (1, 300),
        'route_planning.max_locations': (1, 50),
        'geo_service.cache_ttl': (60, 86400)  # 1分钟到1天
    }
    
    # 允许的枚举值
    FIELD_ENUMS = {
        'route_planning.default_style': ['artistic', 'realistic', 'minimalist', 'vintage'],
        'geo_service.provider': ['openstreetmap', 'google', 'baidu']
    }
    
    @classmethod
    def validate_config_file(cls, config_path: str) -> Dict[str, Any]:
        """
        验证并加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            验证后的配置字典
            
        Raises:
            ConfigValidationError: 配置验证失败
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(config_path):
                raise ConfigValidationError(f"配置文件不存在: {config_path}")
            
            # 检查文件权限
            cls._check_file_permissions(config_path)
            
            # 加载YAML文件
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                raise ConfigValidationError("配置文件为空或格式错误")
            
            # 验证配置结构
            cls._validate_structure(config)
            
            # 验证字段类型
            cls._validate_types(config)
            
            # 验证字段值范围
            cls._validate_ranges(config)
            
            # 验证枚举值
            cls._validate_enums(config)
            
            # 验证业务逻辑
            cls._validate_business_logic(config)
            
            logger.info(f"配置文件验证成功: {config_path}")
            return config
            
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"YAML格式错误: {e}")
        except Exception as e:
            if isinstance(e, ConfigValidationError):
                raise
            raise ConfigValidationError(f"配置文件验证失败: {e}")
    
    @classmethod
    def _check_file_permissions(cls, config_path: str):
        """检查配置文件权限"""
        file_stat = os.stat(config_path)
        file_mode = file_stat.st_mode & 0o777
        
        # 检查文件权限是否过于宽松（不应该对组和其他用户可读）
        if file_mode & 0o077:
            logger.warning(f"配置文件权限过于宽松: {oct(file_mode)}, 建议设置为600")
    
    @classmethod
    def _validate_structure(cls, config: Dict[str, Any]):
        """验证配置结构"""
        for section, required_fields in cls.REQUIRED_FIELDS.items():
            if section not in config:
                raise ConfigValidationError(f"缺少必需的配置节: {section}")
            
            section_config = config[section]
            if not isinstance(section_config, dict):
                raise ConfigValidationError(f"配置节必须是字典类型: {section}")
            
            for field in required_fields:
                if field not in section_config:
                    raise ConfigValidationError(f"缺少必需的配置字段: {section}.{field}")
    
    @classmethod
    def _validate_types(cls, config: Dict[str, Any]):
        """验证字段类型"""
        for field_path, expected_type in cls.FIELD_TYPES.items():
            value = cls._get_nested_value(config, field_path)
            if value is not None:
                if not isinstance(value, expected_type):
                    raise ConfigValidationError(
                        f"字段类型错误: {field_path}, 期望 {expected_type}, 实际 {type(value)}"
                    )
    
    @classmethod
    def _validate_ranges(cls, config: Dict[str, Any]):
        """验证字段值范围"""
        for field_path, (min_val, max_val) in cls.FIELD_RANGES.items():
            value = cls._get_nested_value(config, field_path)
            if value is not None:
                if not (min_val <= value <= max_val):
                    raise ConfigValidationError(
                        f"字段值超出范围: {field_path}={value}, 允许范围 [{min_val}, {max_val}]"
                    )
    
    @classmethod
    def _validate_enums(cls, config: Dict[str, Any]):
        """验证枚举值"""
        for field_path, allowed_values in cls.FIELD_ENUMS.items():
            value = cls._get_nested_value(config, field_path)
            if value is not None:
                if value not in allowed_values:
                    raise ConfigValidationError(
                        f"字段值不在允许范围内: {field_path}={value}, 允许值 {allowed_values}"
                    )
    
    @classmethod
    def _validate_business_logic(cls, config: Dict[str, Any]):
        """验证业务逻辑"""
        # 验证API URL格式
        api_url = config.get('llm', {}).get('api_url', '')
        if api_url and not (api_url.startswith('http://') or api_url.startswith('https://')):
            raise ConfigValidationError(f"API URL格式错误: {api_url}")
        
        # 验证API密钥格式（不为空且长度合理）
        api_key = config.get('llm', {}).get('api_key', '')
        if not api_key or len(api_key) < 10:
            raise ConfigValidationError("API密钥格式错误或过短")
        
        # 验证模型名称格式
        model = config.get('llm', {}).get('model', '')
        if not model or len(model) < 3:
            raise ConfigValidationError("模型名称格式错误")
    
    @classmethod
    def _get_nested_value(cls, config: Dict[str, Any], field_path: str) -> Any:
        """获取嵌套字段值"""
        keys = field_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    @classmethod
    def create_example_config(cls, output_path: str):
        """创建示例配置文件"""
        example_config = {
            'llm': {
                'api_key': 'your-api-key-here',
                'api_url': 'https://your-llm-service.com/api/v1',
                'model': 'gpt-4o-mini',
                'max_tokens': 1000,
                'temperature': 0.3,
                'timeout': 30
            },
            'route_planning': {
                'max_locations': 20,
                'default_style': 'artistic',
                'enable_optimization': True
            },
            'geo_service': {
                'provider': 'openstreetmap',
                'cache_enabled': True,
                'cache_ttl': 3600
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(example_config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"示例配置文件已创建: {output_path}")


def load_and_validate_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载并验证配置文件的便捷函数
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认路径
        
    Returns:
        验证后的配置字典
    """
    if config_path is None:
        # 默认配置文件路径
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config', 'llm_config.yaml'
        )
    
    return ConfigValidator.validate_config_file(config_path)


if __name__ == "__main__":
    # 测试配置验证
    import sys
    
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        try:
            config = load_and_validate_config(config_path)
            print("✅ 配置文件验证成功")
            print(f"模型: {config['llm']['model']}")
            print(f"最大地点数: {config['route_planning']['max_locations']}")
        except ConfigValidationError as e:
            print(f"❌ 配置验证失败: {e}")
            sys.exit(1)
    else:
        print("用法: python config_validator.py <config_file_path>")