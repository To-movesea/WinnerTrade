<template>
  <div class="dashboard">
    <el-row :gutter="24">
      <el-col :span="8">
        <el-card class="stat-card gradient-card-1">
          <div class="stat-content">
            <div class="stat-label">持仓总市值</div>
            <div class="stat-value">¥ 1,245,670</div>
            <div class="stat-footer">
              <span class="trend up">
                <el-icon><CaretTop /></el-icon> +2.5%
              </span>
              <span class="period">较昨日</span>
            </div>
          </div>
          <div class="card-icon">
            <el-icon><Money /></el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card gradient-card-2">
          <div class="stat-content">
            <div class="stat-label">今日盈亏</div>
            <div class="stat-value up">+¥ 32,450</div>
            <div class="stat-footer">
              <span class="trend up">
                <el-icon><CaretTop /></el-icon> 盈利中
              </span>
            </div>
          </div>
          <div class="card-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card gradient-card-3">
          <div class="stat-content">
            <div class="stat-label">持仓股数</div>
            <div class="stat-value">5</div>
            <div class="stat-footer">
              <span class="period">当前仓位</span>
              <span class="trend neutral">65%</span>
            </div>
          </div>
          <div class="card-icon">
            <el-icon><PieChart /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" style="margin-top: 30px;">
      <el-col :span="16">
        <el-card class="action-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon><Lightning /></el-icon> 快速操作
              </span>
            </div>
          </template>
          <div class="action-buttons">
            <el-button type="primary" size="large" class="big-btn" @click="triggerAnalysis" :loading="analyzing">
              <div class="btn-content">
                <el-icon class="btn-icon"><DataAnalysis /></el-icon>
                <div class="btn-text">
                  <span>一键分析持仓</span>
                  <small>调用AI模型分析所有持仓股票</small>
                </div>
              </div>
            </el-button>
            <el-button type="info" size="large" class="big-btn" @click="$router.push('/portfolio/manage')">
              <div class="btn-content">
                <el-icon class="btn-icon"><List /></el-icon>
                <div class="btn-text">
                  <span>添加持仓股</span>
                  <small>管理您的持仓股票列表</small>
                </div>
              </div>
            </el-button>
            <el-button type="success" size="large" class="big-btn" @click="$router.push('/search')">
              <div class="btn-content">
                <el-icon class="btn-icon"><Search /></el-icon>
                <div class="btn-text">
                  <span>查询个股</span>
                  <small>分析任意A股股票行情</small>
                </div>
              </div>
            </el-button>
            <el-button type="warning" size="large" class="big-btn" @click="$router.push('/experience')">
              <div class="btn-content">
                <el-icon class="btn-icon"><Notebook /></el-icon>
                <div class="btn-text">
                  <span>管理经验库</span>
                  <small>定制您的AI反思规则</small>
                </div>
              </div>
            </el-button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="status-card">
          <template #header>
            <div class="card-header">
              <span class="header-title">
                <el-icon><Cpu /></el-icon> 系统状态
              </span>
            </div>
          </template>
          <div class="status-list">
            <div class="status-item">
              <span class="label">API连接</span>
              <el-tag type="success" effect="dark" round>连接正常</el-tag>
            </div>
            <div class="status-item">
              <span class="label">上次分析</span>
              <span class="value">{{ systemStatus.last_analysis || '未执行' }}</span>
            </div>
            <div class="status-item">
              <span class="label">经验规则</span>
              <span class="value highlight">{{ systemStatus.total_rules }} 条</span>
            </div>
            <div class="status-item">
              <span class="label">下次更新</span>
              <span class="value">15:00:00</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const analyzing = ref(false)
const systemStatus = ref({
  last_analysis: '',
  total_rules: 0
})

const fetchStatus = async () => {
  try {
    const res = await axios.get('/api/system/status')
    systemStatus.value = res.data
  } catch (error) {
    console.error('Failed to fetch system status', error)
  }
}

const triggerAnalysis = async () => {
  analyzing.value = true
  try {
    await axios.get('/api/portfolio/analysis')
    ElMessage.success('持仓分析完成')
    fetchStatus()
  } catch (error) {
    ElMessage.error('分析失败: ' + error.message)
  } finally {
    analyzing.value = false
  }
}

onMounted(() => {
  fetchStatus()
})
</script>

<style scoped>
.dashboard {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.stat-card {
  position: relative;
  overflow: hidden;
  height: 160px;
}

.gradient-card-1 {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1), rgba(64, 158, 255, 0.05)) !important;
  border: 1px solid rgba(64, 158, 255, 0.2) !important;
}

.gradient-card-2 {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1), rgba(103, 194, 58, 0.05)) !important;
  border: 1px solid rgba(103, 194, 58, 0.2) !important;
}

.gradient-card-3 {
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.1), rgba(230, 162, 60, 0.05)) !important;
  border: 1px solid rgba(230, 162, 60, 0.2) !important;
}

.stat-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: space-between;
}

.stat-label {
  font-size: 14px;
  color: var(--text-color-secondary);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-color);
  margin: 10px 0;
  letter-spacing: -1px;
}

.stat-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.trend {
  display: flex;
  align-items: center;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.trend.up {
  color: #67c23a;
  background: rgba(103, 194, 58, 0.15);
}

.trend.down {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.15);
}

.trend.neutral {
  color: #e6a23c;
  background: rgba(230, 162, 60, 0.15);
}

.period {
  color: var(--text-color-secondary);
}

.card-icon {
  position: absolute;
  right: -10px;
  bottom: -20px;
  font-size: 120px;
  opacity: 0.05;
  transform: rotate(-15deg);
  z-index: 1;
  pointer-events: none;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.big-btn {
  height: auto !important;
  padding: 20px !important;
  justify-content: flex-start !important;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 15px;
  text-align: left;
}

.btn-icon {
  font-size: 24px;
  background: rgba(255, 255, 255, 0.2);
  padding: 10px;
  border-radius: 12px;
}

.btn-text {
  display: flex;
  flex-direction: column;
}

.btn-text span {
  font-size: 16px;
  font-weight: 600;
}

.btn-text small {
  font-size: 12px;
  opacity: 0.8;
  font-weight: normal;
  margin-top: 4px;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.status-item:last-child {
  border-bottom: none;
}

.status-item .label {
  color: var(--text-color-secondary);
}

.status-item .value {
  font-weight: 600;
}

.status-item .value.highlight {
  color: var(--el-color-primary);
  font-size: 18px;
}
</style>