<template>
  <div class="home">
    <LocationParser @location-parsed="handleLocationParsed" />
    <VisualRenderer 
      v-if="locations.length > 0" 
      :locations="locations" 
    />
    
    <!-- 添加测试路由链接 -->
    <div class="test-link" style="text-align: center; margin: 20px;">
      <router-link to="/test-route" class="test-btn">
        🧪 查看真实路线测试案例
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LocationParser from '@/components/LocationParser.vue'
import VisualRenderer from '@/components/VisualRenderer.vue'
import type { LocationInfo } from '@/types/location'

const locations = ref<LocationInfo[]>([])

const handleLocationParsed = (result: any) => {
  if (result.success && result.location) {
    // 单个地点解析
    const location: LocationInfo = {
      name: result.location.name,
      coordinates: result.location.coordinates,
      address: result.location.address
    }
    locations.value = [location]
  } else if (result.summary && result.results) {
    // 批量解析结果
    const parsedLocations: LocationInfo[] = []
    result.results.forEach((item: any) => {
      if (item.success && item.location) {
        parsedLocations.push({
          name: item.location.name,
          coordinates: item.location.coordinates,
          address: item.location.address
        })
      }
    })
    locations.value = parsedLocations
  }
}
</script>

<style scoped>
.test-btn {
  display: inline-block;
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.test-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}
</style>