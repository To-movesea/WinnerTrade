<template>
  <div class="portfolio">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="header-title">
            <el-icon><PieChart /></el-icon> 持仓股票深度分析
          </span>
          <el-button type="primary" round @click="fetchData" :loading="loading">
            <el-icon class="is-loading" v-if="loading"><Loading /></el-icon>
            <el-icon v-else><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </template>

      <el-table 
        :data="stocks" 
        style="width: 100%" 
        v-loading="loading"
        element-loading-background="rgba(0, 0, 0, 0.5)"
      >
        <el-table-column prop="stock_code" label="代码" width="100">
          <template #default="{ row }">
            <span class="stock-code">{{ row.stock_code }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock_name" label="名称" width="120">
          <template #default="{ row }">
            <span class="stock-name">{{ row.stock_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="现价" width="100">
          <template #default="{ row }">
            <span class="stock-price">{{ row.current_price }}</span>
          </template>
        </el-table-column>
        <el-table-column label="AI评分" width="120" sortable prop="score">
          <template #default="{ row }">
            <div class="score-wrapper">
              <el-progress 
                type="dashboard" 
                :percentage="row.score" 
                :width="40" 
                :stroke-width="4"
                :color="getScoreColor(row.score)"
                :show-text="false"
              />
              <span class="score-text" :style="{ color: getScoreColor(row.score) }">{{ row.score }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="recommendation" label="建议" width="120">
          <template #default="{ row }">
            <el-tag :type="getRecType(row.recommendation)" effect="dark" round>
              {{ row.recommendation }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="关键点位" width="180">
          <template #default="{ row }">
            <div class="price-levels">
              <div class="level-item pressure">
                <span class="label">压</span>
                <span class="value">{{ row.pressure_level }}</span>
              </div>
              <div class="level-item support">
                <span class="label">支</span>
                <span class="value">{{ row.support_level }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="volume_status" label="成交量" width="120">
          <template #default="{ row }">
            <span :class="['volume-tag', getVolumeClass(row.volume_status)]">
              {{ row.volume_status }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="sector_flow" label="板块资金" />
        <el-table-column label="经验警示" min-width="200">
          <template #default="{ row }">
            <div v-if="row.matched_rules" class="warning-tags">
              <el-tooltip
                v-for="(rule, index) in row.matched_rules.split('|')" 
                :key="index"
                effect="dark"
                :content="rule"
                placement="top"
              >
                <el-tag 
                  type="danger" 
                  effect="plain"
                  class="warning-tag"
                >
                  <el-icon><Warning /></el-icon> {{ rule }}
                </el-tag>
              </el-tooltip>
            </div>
            <span v-else class="text-gray-400 safe-text">
              <el-icon><CircleCheck /></el-icon> 无风险提示
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(false)
const stocks = ref([])

const fetchData = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/portfolio/analysis')
    stocks.value = res.data.stocks
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const getScoreColor = (score) => {
  if (score >= 80) return '#f56c6c' // High score usually means strong buy in some contexts, or overbought. Let's assume High=Good=Red in China market context
  if (score >= 60) return '#e6a23c'
  return '#67c23a' // Low score = Green
}

const getRecType = (rec) => {
  if (rec.includes('推荐') || rec.includes('买入')) return 'danger'
  if (rec.includes('卖出')) return 'success'
  return 'info'
}

const getVolumeClass = (status) => {
  if (status.includes('放量')) return 'text-red'
  if (status.includes('缩量')) return 'text-green'
  return ''
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-code {
  font-family: 'Roboto Mono', monospace;
  color: var(--text-color-secondary);
}

.stock-name {
  font-weight: 600;
  font-size: 15px;
}

.stock-price {
  font-family: 'Roboto Mono', monospace;
  font-weight: 600;
  color: #e6a23c;
}

.score-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
}

.score-text {
  position: absolute;
  font-size: 12px;
  font-weight: bold;
}

.price-levels {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.level-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.level-item .label {
  padding: 1px 4px;
  border-radius: 4px;
  font-size: 11px;
  color: #fff;
}

.level-item.pressure .label {
  background-color: rgba(245, 108, 108, 0.6);
}

.level-item.support .label {
  background-color: rgba(103, 194, 58, 0.6);
}

.level-item .value {
  font-family: 'Roboto Mono', monospace;
}

.volume-tag {
  font-weight: 500;
}

.text-red { color: #f56c6c; }
.text-green { color: #67c23a; }

.warning-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.warning-tag {
  cursor: help;
  display: flex;
  align-items: center;
  gap: 4px;
}

.safe-text {
  color: var(--text-color-secondary);
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
}
</style>