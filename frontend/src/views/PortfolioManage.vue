<template>
  <div class="portfolio-manage">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-title">
            <el-icon><List /></el-icon> 管理持仓股票
          </div>
          <el-button type="primary" @click="dialogVisible = true">
            <el-icon><Plus /></el-icon> 添加股票
          </el-button>
        </div>
      </template>

      <el-table :data="stocks" v-loading="loading" style="width: 100%">
        <el-table-column prop="code" label="股票代码" width="100" />
        <el-table-column prop="name" label="股票名称" width="120" />
        <el-table-column label="添加时间" width="170">
            <template #default="{ row }">
                {{ formatTime(row.add_time) }}
            </template>
        </el-table-column>
        <el-table-column prop="cost" label="持仓成本" width="100" />
        <el-table-column prop="motivation" label="买入动机" min-width="150" show-overflow-tooltip />
        <el-table-column prop="risk_sell_time" label="风险卖出时间" width="150" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="deleteStock(row.code)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Add Dialog -->
    <el-dialog v-model="dialogVisible" title="添加持仓股票" width="500px">
      <el-form :model="form" label-width="100px" @submit.prevent="addStock">
        <el-form-item label="股票代码" required>
          <el-input 
            v-model="form.code" 
            placeholder="例如: 600519 或 00700" 
            @keyup.enter="addStock"
          />
        </el-form-item>
        <el-form-item label="持仓成本">
          <el-input v-model="form.cost" placeholder="默认为 未知" />
        </el-form-item>
        <el-form-item label="买入动机">
          <el-input type="textarea" v-model="form.motivation" placeholder="默认为 无" />
        </el-form-item>
        <el-form-item label="风险卖出时间">
           <el-input v-model="form.risk_sell_time" placeholder="默认为 无" />
        </el-form-item>
        <div class="form-tip">支持 A股 (如 600519) 和 港股 (如 00700)</div>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="addStock" :loading="adding">
            添加
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Edit Dialog -->
    <el-dialog v-model="editDialogVisible" title="编辑持仓信息" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="股票名称">
          <span>{{ editForm.name }} ({{ editForm.code }})</span>
        </el-form-item>
        <el-form-item label="持仓成本">
          <el-input v-model="editForm.cost" />
        </el-form-item>
        <el-form-item label="买入动机">
          <el-input type="textarea" v-model="editForm.motivation" />
        </el-form-item>
        <el-form-item label="风险卖出时间">
           <el-input v-model="editForm.risk_sell_time" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateStock" :loading="updating">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const stocks = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const adding = ref(false)

const editDialogVisible = ref(false)
const updating = ref(false)

const form = reactive({
  code: '',
  cost: '未知',
  motivation: '无',
  risk_sell_time: '无'
})

const editForm = reactive({
  code: '',
  name: '',
  cost: '',
  motivation: '',
  risk_sell_time: ''
})

const formatTime = (timeStr) => {
    if (!timeStr) return '--'
    try {
        return new Date(timeStr).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })
    } catch (e) {
        return timeStr
    }
}

const fetchStocks = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/portfolio')
    stocks.value = res.data
  } catch (error) {
    ElMessage.error('加载持仓失败')
  } finally {
    loading.value = false
  }
}

const addStock = async () => {
  if (!form.code) return
  
  adding.value = true
  try {
    await axios.post('/api/portfolio', { 
        stock_code: form.code,
        cost: form.cost || '未知',
        motivation: form.motivation || '无',
        risk_sell_time: form.risk_sell_time || '无'
    })
    ElMessage.success('添加成功')
    dialogVisible.value = false
    
    // Reset form
    form.code = ''
    form.cost = '未知'
    form.motivation = '无'
    form.risk_sell_time = '无'
    
    fetchStocks()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '添加失败，请检查股票代码')
  } finally {
    adding.value = false
  }
}

const openEditDialog = (row) => {
    editForm.code = row.code
    editForm.name = row.name
    editForm.cost = row.cost
    editForm.motivation = row.motivation
    editForm.risk_sell_time = row.risk_sell_time
    editDialogVisible.value = true
}

const updateStock = async () => {
    updating.value = true
    try {
        await axios.put(`/api/portfolio/${editForm.code}`, {
            cost: editForm.cost,
            motivation: editForm.motivation,
            risk_sell_time: editForm.risk_sell_time
        })
        ElMessage.success('更新成功')
        editDialogVisible.value = false
        fetchStocks()
    } catch (error) {
        ElMessage.error(error.response?.data?.error || '更新失败')
    } finally {
        updating.value = false
    }
}

const deleteStock = (code) => {
  ElMessageBox.confirm(`确定删除股票 ${code} 吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await axios.delete(`/api/portfolio/${code}`)
      ElMessage.success('删除成功')
      fetchStocks()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

onMounted(() => {
  fetchStocks()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-title {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: -10px;
  margin-bottom: 20px;
  margin-left: 100px; /* Align with input */
}
</style>