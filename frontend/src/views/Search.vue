<template>
  <div class="search-page">
    <div class="search-hero">
      <h1 class="page-title">智能个股诊断</h1>
      <p class="page-subtitle">输入股票代码，AI助手即刻为您提供深度技术分析与风险预警</p>
      
      <div class="search-box">
        <el-input 
          v-model="searchCode" 
          placeholder="请输入股票代码 (如 600519)" 
          @keyup.enter="searchStock"
          class="custom-search-input"
          size="large"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" @click="searchStock" :loading="loading" class="search-btn">
          立即分析
        </el-button>
      </div>
    </div>

    <transition name="el-zoom-in-center">
      <div v-if="result" class="result-container">
        <el-card class="result-card">
          <div class="result-header">
            <div class="stock-info">
              <h2 class="stock-name">{{ result.stock_name }}</h2>
              <span class="stock-code">{{ result.stock_code }}</span>
            </div>
            <div class="score-badge" :class="getScoreClass(result.score)">
              <div class="score-label">AI评分</div>
              <div class="score-val">{{ result.score }}</div>
            </div>
          </div>

          <el-divider border-style="dashed" />

          <div class="analysis-grid">
            <div class="analysis-item">
              <span class="label">操作建议</span>
              <span class="value recommendation" :class="getRecClass(result.recommendation)">{{ result.recommendation }}</span>
            </div>
            <div class="analysis-item">
              <span class="label">压力位</span>
              <span class="value red">{{ result.pressure_level }}</span>
            </div>
            <div class="analysis-item">
              <span class="label">支撑位</span>
              <span class="value green">{{ result.support_level }}</span>
            </div>
            <div class="analysis-item">
              <span class="label">成交量</span>
              <span class="value">{{ result.volume_status }}</span>
            </div>
            <div class="analysis-item full-width">
              <span class="label">板块资金</span>
              <span class="value">{{ result.sector_flow }}</span>
            </div>
          </div>

          <div v-if="result.matched_rules" class="risk-section">
            <div class="section-title">
              <el-icon><WarningFilled /></el-icon> 风险预警
            </div>
            <div class="risk-list">
              <div 
                v-for="(rule, index) in result.matched_rules.split('|')"
                :key="index"
                class="risk-item"
              >
                <div class="risk-icon">!</div>
                <div class="risk-content">{{ rule }}</div>
              </div>
            </div>
          </div>
          
          <div v-else class="safe-section">
             <el-icon><CircleCheckFilled /></el-icon> 未触发经验库风险规则
          </div>
        </el-card>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const searchCode = ref('')
const loading = ref(false)
const result = ref(null)

const searchStock = async () => {
  if (!searchCode.value) return
  loading.value = true
  result.value = null
  try {
    const res = await axios.get(`/api/stock/analysis/${searchCode.value}`)
    result.value = res.data
  } catch (error) {
    ElMessage.error('分析失败，请检查股票代码')
  } finally {
    loading.value = false
  }
}

const getScoreClass = (score) => {
  if (score >= 80) return 'high'
  if (score >= 60) return 'medium'
  return 'low'
}

const getRecClass = (rec) => {
  if (rec.includes('推荐') || rec.includes('买入')) return 'text-red'
  if (rec.includes('卖出')) return 'text-green'
  return ''
}
</script>

<style scoped>
.search-page {
  max-width: 800px;
  margin: 0 auto;
}

.search-hero {
  text-align: center;
  padding: 40px 0;
}

.page-title {
  font-size: 32px;
  margin-bottom: 10px;
  background: linear-gradient(to right, #409eff, #36cfc9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-subtitle {
  color: var(--text-color-secondary);
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  gap: 15px;
  max-width: 600px;
  margin: 0 auto;
}

.custom-search-input :deep(.el-input__wrapper) {
  padding: 5px 15px;
  font-size: 16px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
}

.search-btn {
  padding: 0 30px;
  font-size: 16px;
}

.result-container {
  margin-top: 20px;
}

.result-card {
  border-radius: 20px !important;
  padding: 10px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.stock-name {
  font-size: 24px;
  margin: 0;
}

.stock-code {
  color: var(--text-color-secondary);
  font-family: 'Roboto Mono';
  font-size: 16px;
}

.stock-price-tag {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 10px;
  font-family: 'Roboto Mono';
  font-weight: 600;
  color: #e6a23c;
}

.score-badge {
  text-align: center;
  padding: 10px 20px;
  border-radius: 12px;
  color: white;
}

.score-badge.high { background: linear-gradient(135deg, #f56c6c, #f78989); box-shadow: 0 4px 15px rgba(245, 108, 108, 0.3); }
.score-badge.medium { background: linear-gradient(135deg, #e6a23c, #f3d19e); box-shadow: 0 4px 15px rgba(230, 162, 60, 0.3); }
.score-badge.low { background: linear-gradient(135deg, #67c23a, #85ce61); box-shadow: 0 4px 15px rgba(103, 194, 58, 0.3); }

.score-label { font-size: 12px; opacity: 0.9; }
.score-val { font-size: 28px; font-weight: bold; line-height: 1; }

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin: 20px 0;
}

.analysis-item {
  background: rgba(255, 255, 255, 0.03);
  padding: 15px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.analysis-item.full-width {
  grid-column: span 2;
}

.analysis-item .label {
  color: var(--text-color-secondary);
  font-size: 13px;
  margin-bottom: 5px;
}

.analysis-item .value {
  font-size: 18px;
  font-weight: 600;
}

.text-red, .red { color: #f56c6c; }
.text-green, .green { color: #67c23a; }
.recommendation { font-size: 20px; }

.risk-section {
  margin-top: 25px;
  background: rgba(245, 108, 108, 0.1);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(245, 108, 108, 0.2);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f56c6c;
  font-weight: bold;
  margin-bottom: 15px;
}

.risk-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.risk-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.risk-icon {
  background: #f56c6c;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
  flex-shrink: 0;
}

.safe-section {
  margin-top: 25px;
  text-align: center;
  color: #67c23a;
  background: rgba(103, 194, 58, 0.1);
  padding: 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
</style>