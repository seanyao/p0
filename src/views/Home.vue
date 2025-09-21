<template>
  <div class="home">
    <LocationParser
      :placeholder="'请输入地名，如：北京市朝阳区、上海外滩、西湖'"
      :show-history="true"
      :show-batch-mode="true"
      @location-parsed="handleLocationParsed"
      @error="handleError"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 首页视图组件
 */

import LocationParser from '../components/LocationParser.vue'

const handleLocationParsed = (result: any) => {
  console.log('地名解析结果:', result)
}

const handleError = (error: string) => {
  console.error('解析错误:', error)
}
</script>

<style scoped>
.home {
  padding: 1rem;
}
</style>