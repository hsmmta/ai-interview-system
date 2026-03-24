<template>
  <div class="result-container">
    <div class="result-header">
      <h2>面试评估报告</h2>
      <button class="btn-back" @click="goHome">返回首页</button>
    </div>

    <div v-if="loading" class="loading">正在生成评估报告...</div>

    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchResult">重试</button>
    </div>

    <div v-else class="report-content">
      <!-- Overview Section -->
      <div v-if="evaluation.overview" class="section overview-section">
        <h3>综合评分</h3>
        <div class="score-card">
          <div class="score">{{ evaluation.score || 'N/A' }}</div>
          <div class="grade">{{ evaluation.grade || '待定' }}</div>
        </div>
        <p class="summary">{{ evaluation.summary }}</p>
      </div>

      <!-- Detail Section -->
      <div class="section detail-section">
        <h3>详细点评</h3>
        <div class="markdown-body" v-html="formattedEvaluation"></div>
      </div>

      <!-- Q&A Review -->
      <div class="section qa-section">
        <h3>问答回顾</h3>
        <div
          v-for="(q, index) in questions"
          :key="q.id"
          class="qa-item"
        >
          <div class="question">
            <span class="badgem">Q{{ index + 1 }}</span>
            {{ q.question }}
          </div>
          <div class="answer">
            <span class="badgea">A</span>
            {{ answers[index] || '未作答' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const error = ref('')
const resultData = ref(null)

const evaluation = computed(() => {
  if (!resultData.value) return {}
  // Parser logic if needed, or use fields from JSON
  return {
    score: resultData.value.score, // if available
    grade: resultData.value.level,
    summary: resultData.value.summary // if available
  }
})

const questions = computed(() => resultData.value?.questions || [])
const answers = computed(() => resultData.value?.answers || [])

const formattedEvaluation = computed(() => {
  if (!resultData.value?.evaluation?.realtime_evaluation) return ''
  let text = resultData.value.evaluation.realtime_evaluation
  // Simple markdown to HTML
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  text = text.replace(/\n\n/g, '<br><br>')
  text = text.replace(/\n/g, '<br>')
  return text
})

onMounted(() => {
  fetchResult()
})

const fetchResult = async () => {
  loading.value = true
  error.value = ''
  try {
    const sessionId = route.query.sessionId
    if (!sessionId) throw new Error('无效的会话 ID')

    // Fetch result
    const res = await axios.get(`/api/interview/result`, {
      params: { sessionId }
    })

    if (res.data.success) {
      resultData.value = res.data
    } else {
      error.value = res.data.message || '获取结果失败'
    }
  } catch (err) {
    console.error('Fetch result failed', err)
    error.value = '无法加载评估结果，请稍后重试'
  } finally {
    loading.value = false
  }
}

const goHome = () => {
  router.push('/profile')
}
</script>

<style scoped>
.result-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Segoe UI', sans-serif;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}

.btn-back {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.loading, .error-state {
  text-align: center;
  margin-top: 3rem;
  color: #666;
}

.section {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
}

h3 {
  margin-top: 0;
  color: #333;
  border-left: 4px solid #667eea;
  padding-left: 10px;
}

.score-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.score {
  font-size: 3rem;
  font-weight: bold;
  color: #667eea;
}

.grade {
  font-size: 1.5rem;
  background: #f0f2f5;
  padding: 0.2rem 1rem;
  border-radius: 20px;
  color: #555;
}

.markdown-body {
  line-height: 1.8;
  color: #444;
}

.qa-item {
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #f9f9f9;
  padding-bottom: 1rem;
}

.question, .answer {
  margin-bottom: 0.5rem;
  position: relative;
  padding-left: 2rem;
}

.badgem, .badgea {
  position: absolute;
  left: 0;
  top: 0;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  text-align: center;
  line-height: 24px;
  font-size: 0.8rem;
  font-weight: bold;
}

.badgem {
  background: #e6f7ff;
  color: #1890ff;
}

.badgea {
  background: #f6ffed;
  color: #52c41a;
}

.question {
  font-weight: 600;
  color: #333;
}

.answer {
  color: #666;
}
</style>

