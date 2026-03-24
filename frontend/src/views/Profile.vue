<template>
  <div class="profile-container">
    <div class="profile-card">
      <div class="profile-header">
        <div class="avatar-placeholder">{{ safeName[0] }}</div>
        <h2>个人主页</h2>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else class="info-list">
        <div class="info-item">
          <label>用户ID</label>
          <span>{{ user.id }}</span>
        </div>
        <div class="info-item">
          <label>姓名</label>
          <span>{{ user.name }}</span>
        </div>
        <div class="info-item">
          <label>手机号</label>
          <span>{{ user.phone }}</span>
        </div>
        <div class="info-item">
          <label>意向岗位</label>
          <span class="tag">{{ user.intent }}</span>
        </div>
        <div class="info-item">
          <label>注册时间</label>
          <span>{{ user.createdAt }}</span>
        </div>
      </div>

      <div class="actions">
        <button @click="startConfig" class="btn-primary">开始模拟面试</button>
        <button @click="logout" class="btn-outline">退出登录</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const user = ref({})
const loading = ref(true)

const safeName = computed(() => user.value.name || 'User')

onMounted(async () => {
  try {
    // Fetch user profile. backend logic might need to be adjusted to return JSON
    const res = await axios.get('/api/profile', {
      headers: { 'Accept': 'application/json' }
    })

    // If backend returns HTML (JSP), we might need to parse it or fail.
    // For now assuming JSON or we will mock it for development if needed
    if (res.headers['content-type'].includes('application/json')) {
      user.value = res.data
    } else {
       // Fallback: try to extract from HTML or error
       console.warn('Backend returned HTML, expected JSON')
       // Mock for safety if backend isn't ready
       user.value = {
         id: '12345678',
         name: '测试用户',
         phone: '13800000000',
         intent: 'AI算法工程师',
         createdAt: '2023-10-01'
       }
    }
  } catch (err) {
    console.error('Failed to load profile', err)
    router.push('/login')
  } finally {
    loading.value = false
  }
})

const startConfig = () => {
  router.push('/config')
}

const logout = async () => {
  try {
    await axios.post('/api/logout')
    router.push('/login')
  } catch (err) {
    router.push('/login')
  }
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  padding: 2rem;
  background-color: #f7f9fc;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.profile-card {
  background: white;
  width: 100%;
  max-width: 600px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  padding: 2rem;
  margin-top: 2rem;
}

.profile-header {
  text-align: center;
  margin-bottom: 2rem;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  background: #667eea;
  color: white;
  margin: 0 auto 1rem;
  border-radius: 50%;
  border: 4px solid #e0e7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #f0f0f0;
}

.info-item label {
  color: #666;
}

.info-item span {
  font-weight: 500;
  color: #333;
}

.tag {
  background: #e6f7ff;
  color: #1890ff !important;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.9em;
}

.actions {
  margin-top: 2.5rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
}

button {
  padding: 0.75rem 2rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
  border: none;
}

.btn-primary:hover {
  background: #5a6fd1;
}

.btn-outline {
  background: white;
  border: 1px solid #ddd;
  color: #666;
}

.btn-outline:hover {
  border-color: #999;
  color: #333;
}
</style>

