<template>
  <el-container class="layout-container">
    <el-header class="glass-header">
      <div class="logo">
        <div class="logo-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <span class="logo-text">五七股票助手</span>
      </div>
      <el-menu
        :default-active="activeIndex"
        mode="horizontal"
        router
        :ellipsis="false"
      >
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon> 持仓概览
        </el-menu-item>
        <el-menu-item index="/portfolio">
          <el-icon><PieChart /></el-icon> 持仓分析
        </el-menu-item>
        <el-menu-item index="/search">
          <el-icon><Search /></el-icon> 股票查询
        </el-menu-item>
        <el-menu-item index="/experience">
          <el-icon><Notebook /></el-icon> 经验库
        </el-menu-item>
      </el-menu>
    </el-header>
    
    <el-main>
      <router-view v-slot="{ Component }">
        <transition name="fade-slide" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeIndex = computed(() => route.path)
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background-color: var(--bg-color);
}

.glass-header {
  background: rgba(43, 43, 47, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 70px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
}

/* 增强导航栏文字对比度 */
.glass-header :deep(.el-menu) {
  background: transparent;
  border-bottom: none;
  --el-menu-text-color: #e5eaf3;
  --el-menu-hover-text-color: #ffffff;
  --el-menu-bg-color: transparent;
  --el-menu-hover-bg-color: rgba(255, 255, 255, 0.05);
  --el-menu-active-color: #409eff;
}

.glass-header :deep(.el-menu-item) {
  font-size: 15px;
  font-weight: 500;
}

.glass-header :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.05) !important;
  color: #ffffff !important;
}

.glass-header :deep(.el-menu-item.is-active) {
  border-bottom: 2px solid #409eff;
  color: #409eff !important;
  background: transparent !important;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(64, 158, 255, 0.3);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  background: linear-gradient(135deg, #409eff, #36cfc9);
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  box-shadow: 0 4px 10px rgba(64, 158, 255, 0.4);
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(to right, #fff, #a3a6ad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 1px;
}

.el-main {
  padding: 30px 40px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>