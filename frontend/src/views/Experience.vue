<template>
  <div class="experience">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="title-group">
            <span class="header-title">
              <el-icon><Notebook /></el-icon> 经验规则库
            </span>
            <el-tag type="info" round effect="plain">共 {{ rules.length }} 条规则</el-tag>
          </div>
          
          <div class="header-actions">
            <el-button-group>
              <el-button type="success" @click="exportRules">
                <el-icon><Download /></el-icon> 备份
              </el-button>
              <el-button type="warning" @click="importRules">
                <el-icon><Upload /></el-icon> 恢复
              </el-button>
            </el-button-group>
            <el-button type="primary" @click="showAddDialog" icon="Plus" circle class="add-btn"></el-button>
          </div>
        </div>
      </template>

      <div class="rules-container" v-loading="loading">
        <el-empty v-if="rules.length === 0" description="暂无经验规则，快去添加吧" />
        
        <div v-else class="rule-grid">
          <div v-for="rule in rules" :key="rule.id" class="rule-card">
            <div class="rule-header">
              <el-tag :type="getCategoryType(rule.category)" effect="dark" size="small">
                {{ getCategoryLabel(rule.category) }}
              </el-tag>
              <div class="rule-actions">
                <el-button link type="primary" @click="editRule(rule)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button link type="danger" @click="deleteRule(rule.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            
            <div class="rule-content">
              {{ rule.rule_content }}
            </div>
            
            <div class="rule-desc" v-if="rule.description">
              {{ rule.description }}
            </div>
            
            <div class="rule-footer">
              <small>创建于 {{ formatDate(rule.created_at) }}</small>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <el-dialog 
      v-model="dialogVisible" 
      :title="editingRule ? '编辑规则' : '新增规则'"
      width="500px"
      destroy-on-close
    >
      <el-form :model="form" label-width="80px" class="custom-form">
        <el-form-item label="规则内容">
          <el-input 
            v-model="form.rule" 
            placeholder="例如：尾盘拉升则次日卖出" 
            type="textarea" 
            :rows="2"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" placeholder="选择分类" style="width: 100%">
            <el-option label="时机选择" value="timing" />
            <el-option label="技术形态" value="technical" />
            <el-option label="成交量" value="volume" />
            <el-option label="板块资金" value="sector" />
          </el-select>
        </el-form-item>
        <el-form-item label="详细说明">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="规则的详细解释或备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRule">确定保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const rules = ref([])
const dialogVisible = ref(false)
const editingRule = ref(null)
const form = reactive({
  rule: '',
  category: 'timing',
  description: ''
})

const fetchRules = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/experience/rules')
    rules.value = res.data
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  editingRule.value = null
  form.rule = ''
  form.category = 'timing'
  form.description = ''
  dialogVisible.value = true
}

const editRule = (row) => {
  editingRule.value = row
  form.rule = row.rule_content
  form.category = row.category
  form.description = row.description
  dialogVisible.value = true
}

const saveRule = async () => {
  try {
    if (editingRule.value) {
      await axios.put(`/api/experience/rules/${editingRule.value.id}`, form)
      ElMessage.success('更新成功')
    } else {
      await axios.post('/api/experience/rules', form)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchRules()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteRule = (id) => {
  ElMessageBox.confirm('确定删除该规则吗?', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    background: true
  }).then(async () => {
    try {
      await axios.delete(`/api/experience/rules/${id}`)
      ElMessage.success('删除成功')
      fetchRules()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const exportRules = async () => {
  try {
    await axios.get('/api/experience/export')
    ElMessage.success('导出成功，已保存到服务器data目录')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const importRules = async () => {
  try {
    await axios.post('/api/experience/import')
    ElMessage.success('导入成功')
    fetchRules()
  } catch (error) {
    ElMessage.error('导入失败')
  }
}

const getCategoryType = (cat) => {
  const map = {
    timing: 'warning',
    technical: 'primary',
    volume: 'danger',
    sector: 'success'
  }
  return map[cat] || 'info'
}

const getCategoryLabel = (cat) => {
  const map = {
    timing: '时机选择',
    technical: '技术形态',
    volume: '成交量',
    sector: '板块资金'
  }
  return map[cat] || cat
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString()
}

onMounted(() => {
  fetchRules()
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

.title-group {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-actions {
  display: flex;
  gap: 15px;
  align-items: center;
}

.add-btn {
  box-shadow: 0 4px 15px rgba(64, 158, 255, 0.4);
}

.rule-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.rule-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 15px;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
}

.rule-card:hover {
  background: rgba(255, 255, 255, 0.06);
  transform: translateY(-3px);
  border-color: rgba(255, 255, 255, 0.1);
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rule-content {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  line-height: 1.4;
  flex-grow: 1;
}

.rule-desc {
  font-size: 13px;
  color: var(--text-color-secondary);
  margin-bottom: 15px;
  line-height: 1.5;
}

.rule-footer {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 10px;
  margin-top: auto;
}
</style>