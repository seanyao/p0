import pytest
import asyncio
from app.services.route_generator import RouteGenerator
from app.models import Coordinate

class TestRouteGenerator:
    """路线生成功能测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.route_generator = RouteGenerator()
        
        # 测试数据：北京 -> 上海 -> 广州
        self.test_coordinates = [
            Coordinate(lng=116.4074, lat=39.9042, name="北京", level="city"),
            Coordinate(lng=121.4737, lat=31.2304, name="上海", level="city"),
            Coordinate(lng=113.2644, lat=23.1291, name="广州", level="city")
        ]
    
    @pytest.mark.asyncio
    async def test_generate_route_basic(self):
        """测试基本路线生成功能"""
        result = await self.route_generator.generate_route(self.test_coordinates)
        
        # 验证返回数据结构
        assert result is not None
        assert len(result.coordinates) == 3
        assert result.bounds is not None
        assert result.center is not None
        assert result.zoom > 0
        assert len(result.pathPoints) > 0
        assert len(result.labelPositions) == 3
    
    @pytest.mark.asyncio
    async def test_generate_route_two_points(self):
        """测试两点路线生成"""
        two_points = self.test_coordinates[:2]
        result = await self.route_generator.generate_route(two_points)
        
        assert len(result.coordinates) == 2
        assert len(result.labelPositions) == 2
        assert result.bounds is not None
    
    @pytest.mark.asyncio
    async def test_generate_route_empty_coordinates(self):
        """测试空坐标列表"""
        with pytest.raises(Exception, match="路线生成失败"):
            await self.route_generator.generate_route([])
    
    @pytest.mark.asyncio
    async def test_generate_route_single_point(self):
        """测试单点路线（应该返回空路径）"""
        single_point = [self.test_coordinates[0]]
        result = await self.route_generator.generate_route(single_point)
        
        assert len(result.coordinates) == 1
        assert len(result.pathPoints) == 0  # 单点无路径
        assert len(result.labelPositions) == 1
    
    def test_calculate_bounds(self):
        """测试边界计算"""
        bounds = self.route_generator.calculate_bounds(self.test_coordinates)
        
        # 验证边界包含所有点
        assert bounds.southwest.lng <= 113.2644  # 广州经度
        assert bounds.northeast.lng >= 121.4737  # 上海经度
        assert bounds.southwest.lat <= 23.1291   # 广州纬度
        assert bounds.northeast.lat >= 39.9042   # 北京纬度
    
    def test_calculate_center(self):
        """测试中心点计算"""
        center = self.route_generator.calculate_center(self.test_coordinates)
        
        # 验证中心点在合理范围内
        assert 113 <= center.lng <= 122
        assert 23 <= center.lat <= 40
    
    def test_calculate_zoom(self):
        """测试缩放级别计算"""
        bounds = self.route_generator.calculate_bounds(self.test_coordinates)
        zoom = self.route_generator.calculate_zoom(bounds)
        
        # 对于跨越中国的路线，缩放级别应该较小
        assert 4.0 <= zoom <= 7.0
    
    def test_generate_path_points(self):
        """测试路径点生成"""
        path_points = self.route_generator.generate_path_points(self.test_coordinates)
        
        # 3个点应该生成多个路径点（包含控制点）
        assert len(path_points) > 3
        
        # 验证路径点类型
        start_points = [p for p in path_points if p.type == 'start']
        control_points = [p for p in path_points if p.type == 'control']
        end_points = [p for p in path_points if p.type == 'end']
        
        assert len(start_points) >= 2  # 至少2个起始点
        assert len(control_points) >= 2  # 至少2个控制点
        assert len(end_points) == 1  # 1个结束点
    
    def test_generate_bezier_control_points(self):
        """测试贝塞尔控制点生成"""
        start = self.test_coordinates[0]  # 北京
        end = self.test_coordinates[1]    # 上海
        
        control_points = self.route_generator.generate_bezier_control_points(start, end)
        
        assert len(control_points) == 2
        
        # 验证控制点在起始点和结束点之间
        for cp in control_points:
            assert min(start.lng, end.lng) <= cp['lng'] <= max(start.lng, end.lng)
            assert min(start.lat, end.lat) <= cp['lat'] <= max(start.lat, end.lat)
    
    def test_optimize_label_positions(self):
        """测试标签位置优化"""
        label_positions = self.route_generator.optimize_label_positions(self.test_coordinates)
        
        assert len(label_positions) == 3
        
        # 验证每个标签都有位置信息
        for label in label_positions:
            assert label.lng is not None
            assert label.lat is not None
            assert label.name is not None
            assert label.offset_x is not None
            assert label.offset_y is not None
    
    def test_calculate_distance(self):
        """测试距离计算"""
        beijing = self.test_coordinates[0]
        shanghai = self.test_coordinates[1]
        
        distance = self.route_generator.calculate_distance(beijing, shanghai)
        
        # 北京到上海的直线距离大约1000公里
        assert 800 < distance < 1500

if __name__ == "__main__":
    # 运行基本测试
    async def run_basic_test():
        generator = RouteGenerator()
        coordinates = [
            Coordinate(lng=116.4074, lat=39.9042, name="北京", level="city"),
            Coordinate(lng=121.4737, lat=31.2304, name="上海", level="city"),
            Coordinate(lng=113.2644, lat=23.1291, name="广州", level="city")
        ]
        
        try:
            result = await generator.generate_route(coordinates)
            print("✅ 路线生成测试通过")
            print(f"   - 坐标数量: {len(result.coordinates)}")
            print(f"   - 路径点数量: {len(result.pathPoints)}")
            print(f"   - 标签数量: {len(result.labelPositions)}")
            print(f"   - 缩放级别: {result.zoom}")
            print(f"   - 中心点: ({result.center.lng:.4f}, {result.center.lat:.4f})")
        except Exception as e:
            print(f"❌ 路线生成测试失败: {e}")
    
    asyncio.run(run_basic_test())