<template>
  <div class="config-container">
    <div class="config-card">
      <h2>面试配置</h2>
      <p class="subtitle">根据您的需求开启模拟面试</p>

      <form @submit.prevent="startInterview">
        <div class="form-group">
          <label>面试方向</label>
          <div class="selection-box">
            {{ userIntent || 'Java后端开发' }}
          </div>
        </div>

        <div class="form-group">
          <label>题目数量</label>
          <div class="input-control">
            <input
              v-model.number="questionCount"
              type="number"
              min="5"
              max="20"
              step="1"
            />
            <span class="helper-text">建议 10-15 题</span>
          </div>
        </div>

        <div class="form-group">
          <label>答题方式</label>
          <div class="mode-selection">
            <div
              class="mode-card"
              :class="{ active: mode === 'text' }"
              @click="mode = 'text'"
            >
              <div class="icon">📝</div>
              <span>文本作答</span>
            </div>
            <div
              class="mode-card"
              :class="{ active: mode === 'voice' }"
              @click="mode = 'voice'"
            >
              <div class="icon">🎙️</div>
              <span>语音作答</span>
            </div>
          </div>
        </div>

        <button type="submit" class="btn-start" :disabled="loading">
          {{ loading ? '生成面试中...' : '开始面试' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const mode = ref('text')
const interviewType = ref('campus')
const questionCount = ref(15)
const userIntent = ref('')
const loading = ref(false)

onMounted(async () => {
  try {
     const res = await axios.get('/api/profile')
     if (res.data && res.data.user && res.data.user.targetPosition) {
       userIntent.value = res.data.user.targetPosition
     } else {
       userIntent.value = 'Java后端开发'
     }
  } catch (e) {
    userIntent.value = 'Java后端开发'
  }
})

const startInterview = async () => {
  loading.value = true
  try {
    // Step 1: Create Session
    const configRes = await axios.post('/api/interview/config', {
      interviewType: interviewType.value,
      direction: userIntent.value,
      questionCount: questionCount.value
    })

    if (!configRes.data.success || !configRes.data.sessionId) {
      throw new Error(configRes.data.error || '创建会话失败')
    }

    const sessionId = configRes.data.sessionId

    // Step 2: Generate Questions
    const genRes = await axios.post('/api/interview/generate', {
      sessionId: sessionId
    })

    if (genRes.data.success || genRes.status === 200) {
      if (genRes.data.questions) {
        sessionStorage.setItem('interviewQuestions', JSON.stringify(genRes.data.questions));
      }

      if (mode.value === 'text') {
        router.push({ path: '/interview', query: { sessionId } })
      } else {
        router.push({ path: '/interview-voice', query: { sessionId } })
      }
    }
  } catch (err) {
    console.error('Failed to start interview', err)
    alert(err.message || '生成题目失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.config-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f7f9fc;
}

.config-card {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.08);
  width: 100%;
  max-width: 500px;
}

h2 {
  text-align: center;
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 2rem;
}

label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #333;
}

.selection-box {
  padding: 1rem;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  color: #495057;
  font-weight: 500;
}

.input-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

input[type="number"] {
  width: 100px;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  text-align: center;
  font-size: 1.1rem;
}

.helper-text {
  color: #868e96;
  font-size: 0.9rem;
}

.mode-selection {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.mode-card {
  border: 2px solid #e9ecef;
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-card:hover {
  border-color: #adb5bd;
}

.mode-card.active {
  border-color: #667eea;
  background-color: #f0f4ff;
  color: #5a6fd1;
}

.icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.btn-start {
  width: 100%;
  padding: 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-start:hover {
  background: #5a6fd1;
}

.btn-start:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}
</style>
