import math
from typing import List, Dict, Optional, Tuple
from app.models import Coordinate, RouteData, PathPoint, MapBounds, LabelPosition

class RouteGenerator:
    """路线生成服务"""
    
    def __init__(self):
        self.cache: Dict[str, RouteData] = {}
    
    async def generate_route(self, coordinates: List[Coordinate]) -> RouteData:
        """生成路线数据"""
        try:
            # 1. 计算地图边界
            bounds = self.calculate_bounds(coordinates)
            
            # 2. 计算地图中心点
            center = self.calculate_center(coordinates)
            
            # 3. 计算缩放级别
            zoom = self.calculate_zoom(bounds)
            
            # 4. 生成路径点
            path_points = self.generate_path_points(coordinates)
            
            # 5. 优化标签位置
            label_positions = self.optimize_label_positions(coordinates)
            
            route_data = RouteData(
                coordinates=coordinates,
                pathPoints=path_points,
                bounds=bounds,
                center=center,
                zoom=zoom,
                labelPositions=label_positions
            )
            
            return route_data
            
        except Exception as e:
            raise Exception(f"路线生成失败: {str(e)}")
    
    def calculate_bounds(self, coordinates: List[Coordinate]) -> MapBounds:
        """计算地图边界"""
        if not coordinates:
            raise ValueError("坐标列表不能为空")
        
        lngs = [coord.lng for coord in coordinates]
        lats = [coord.lat for coord in coordinates]
        
        min_lng = min(lngs)
        max_lng = max(lngs)
        min_lat = min(lats)
        max_lat = max(lats)
        
        # 添加10%的边距
        lng_padding = (max_lng - min_lng) * 0.1 if max_lng != min_lng else 0.01
        lat_padding = (max_lat - min_lat) * 0.1 if max_lat != min_lat else 0.01
        
        southwest = Coordinate(
            lng=min_lng - lng_padding,
            lat=min_lat - lat_padding,
            name="southwest",
            level="district"
        )
        
        northeast = Coordinate(
            lng=max_lng + lng_padding,
            lat=max_lat + lat_padding,
            name="northeast", 
            level="district"
        )
        
        return MapBounds(southwest=southwest, northeast=northeast)
    
    def calculate_center(self, coordinates: List[Coordinate]) -> Coordinate:
        """计算地图中心点"""
        if not coordinates:
            raise ValueError("坐标列表不能为空")
        
        total_lng = sum(coord.lng for coord in coordinates)
        total_lat = sum(coord.lat for coord in coordinates)
        
        center_lng = total_lng / len(coordinates)
        center_lat = total_lat / len(coordinates)
        
        return Coordinate(
            lng=center_lng,
            lat=center_lat,
            name="center",
            level="district"
        )
    
    def calculate_zoom(self, bounds: MapBounds) -> float:
        """计算合适的缩放级别"""
        # 计算经纬度跨度
        lng_span = bounds.northeast.lng - bounds.southwest.lng
        lat_span = bounds.northeast.lat - bounds.southwest.lat
        
        # 根据跨度计算缩放级别（简化算法）
        max_span = max(lng_span, lat_span)
        
        if max_span > 20:
            return 4.0  # 国家级别
        elif max_span > 10:
            return 5.0  # 大区域
        elif max_span > 5:
            return 6.0  # 省级
        elif max_span > 2:
            return 7.0  # 市级
        elif max_span > 1:
            return 8.0  # 区级
        else:
            return 10.0  # 详细级别
    
    def generate_path_points(self, coordinates: List[Coordinate]) -> List[PathPoint]:
        """生成路径点（包含贝塞尔曲线控制点）"""
        if len(coordinates) < 2:
            return []
        
        path_points = []
        
        for i in range(len(coordinates) - 1):
            start = coordinates[i]
            end = coordinates[i + 1]
            
            # 添加起始点
            path_points.append(PathPoint(
                lng=start.lng,
                lat=start.lat,
                type='start',
                index=i * 3
            ))
            
            # 生成贝塞尔曲线控制点
            control_points = self.generate_bezier_control_points(start, end)
            
            for j, control_point in enumerate(control_points):
                path_points.append(PathPoint(
                    lng=control_point['lng'],
                    lat=control_point['lat'],
                    type='control',
                    index=i * 3 + j + 1
                ))
        
        # 添加最后一个点
        last_coord = coordinates[-1]
        path_points.append(PathPoint(
            lng=last_coord.lng,
            lat=last_coord.lat,
            type='end',
            index=len(path_points)
        ))
        
        return path_points
    
    def generate_bezier_control_points(self, start: Coordinate, end: Coordinate) -> List[Dict]:
        """生成贝塞尔曲线控制点"""
        # 计算中点
        mid_lng = (start.lng + end.lng) / 2
        mid_lat = (start.lat + end.lat) / 2
        
        # 计算距离
        distance = self.calculate_distance(start, end)
        
        # 根据距离调整控制点偏移
        offset = min(distance * 0.2, 0.5)  # 最大偏移0.5度
        
        # 计算垂直方向的偏移
        angle = math.atan2(end.lat - start.lat, end.lng - start.lng)
        perpendicular_angle = angle + math.pi / 2
        
        control_point_1 = {
            'lng': mid_lng + offset * math.cos(perpendicular_angle) * 0.5,
            'lat': mid_lat + offset * math.sin(perpendicular_angle) * 0.5
        }
        
        control_point_2 = {
            'lng': mid_lng - offset * math.cos(perpendicular_angle) * 0.5,
            'lat': mid_lat - offset * math.sin(perpendicular_angle) * 0.5
        }
        
        return [control_point_1, control_point_2]
    
    def calculate_distance(self, coord1: Coordinate, coord2: Coordinate) -> float:
        """计算两点间距离（公里）"""
        # 使用Haversine公式计算地球表面两点间的距离
        R = 6371  # 地球半径（公里）
        
        lat1_rad = math.radians(coord1.lat)
        lat2_rad = math.radians(coord2.lat)
        delta_lat = math.radians(coord2.lat - coord1.lat)
        delta_lng = math.radians(coord2.lng - coord1.lng)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def optimize_label_positions(self, coordinates: List[Coordinate]) -> List[LabelPosition]:
        """优化标签位置，避免重叠"""
        label_positions = []
        occupied_areas = []
        
        for coord in coordinates:
            best_position = self.find_best_label_position(coord, occupied_areas)
            label_positions.append(best_position)
            
            # 记录占用区域
            bounds = self.get_label_bounds(best_position)
            occupied_areas.append(bounds)
        
        return label_positions
    
    def find_best_label_position(self, coordinate: Coordinate, occupied_areas: List[Dict]) -> LabelPosition:
        """为坐标点找到最佳标签位置"""
        positions = ['top', 'right', 'bottom', 'left']
        offsets = {
            'top': (0, 20),
            'right': (20, 0),
            'bottom': (0, -20),
            'left': (-20, 0)
        }
        
        for position in positions:
            offset_x, offset_y = offsets[position]
            label_position = LabelPosition(
                lng=coordinate.lng,
                lat=coordinate.lat,
                name=coordinate.name,
                offset_x=offset_x,
                offset_y=offset_y,
                position=position
            )
            
            bounds = self.get_label_bounds(label_position)
            if not self.is_overlapping(bounds, occupied_areas):
                return label_position
        
        # 如果所有位置都重叠，返回默认位置
        return LabelPosition(
            lng=coordinate.lng,
            lat=coordinate.lat,
            name=coordinate.name,
            offset_x=0,
            offset_y=20,
            position='top'
        )
    
    def get_label_bounds(self, label_position: LabelPosition) -> Dict:
        """获取标签的边界框"""
        # 估算标签尺寸（基于文本长度）
        text_length = len(label_position.name)
        width = max(0.01, text_length * 0.002)  # 根据文本长度估算宽度
        height = 0.005  # 固定高度
        
        return {
            'x': label_position.lng + label_position.offset_x * 0.001,
            'y': label_position.lat + label_position.offset_y * 0.001,
            'width': width,
            'height': height
        }
    
    def is_overlapping(self, bounds1: Dict, occupied_areas: List[Dict]) -> bool:
        """检查边界框是否与已占用区域重叠"""
        for bounds2 in occupied_areas:
            if (bounds1['x'] < bounds2['x'] + bounds2['width'] and
                bounds1['x'] + bounds1['width'] > bounds2['x'] and
                bounds1['y'] < bounds2['y'] + bounds2['height'] and
                bounds1['y'] + bounds1['height'] > bounds2['y']):
                return True
        return False
    
    def optimize_layout(self, route: RouteData) -> RouteData:
        """优化整体布局"""
        # 重新计算标签位置以避免与路径重叠
        optimized_labels = self.optimize_label_positions(route.coordinates)
        
        route.labelPositions = optimized_labels
        return route