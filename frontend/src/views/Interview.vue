<template>
  <div class="interview-container">
    <div class="sidebar">
      <h3>题目列表</h3>
      <ul class="question-list">
        <li
          v-for="(q, index) in questions"
          :key="q.id"
          :class="{ active: index === currentIndex, completed: isAnswered(index) }"
          @click="jumpTo(index)"
        >
          <span class="status-dot"></span>
          第 {{ index + 1 }} 题
        </li>
      </ul>
      <button class="btn-submit-all" @click="submitAll">提交所有回答</button>
    </div>

    <div class="main-content">
      <div v-if="currentQuestion" class="question-card">
        <div class="card-header">
          <span class="question-number">{{ currentIndex + 1 }}/{{ questions.length }}</span>
          <span class="question-type">{{ currentQuestion.type === 'coding' ? '编程题' : '简答题' }}</span>
        </div>

        <div class="question-body">
          <p class="question-text">{{ currentQuestion.question }}</p>
        </div>

        <div class="answer-area">
          <textarea
            v-model="answers[currentIndex]"
            placeholder="在此输入您的回答..."
            rows="10"
          ></textarea>
        </div>

        <div class="card-footer">
          <button
            type="button"
            class="btn-nav btn-prev"
            :disabled="currentIndex === 0"
            @click="prevQuestion"
          >
            上一题
          </button>

          <button
            v-if="currentIndex < questions.length - 1"
            type="button"
            class="btn-nav btn-next"
            @click="nextQuestion"
          >
            下一题
          </button>
          <button
            v-else
            type="button"
            class="btn-nav btn-submit"
            @click="submitAll"
          >
            提交试卷
          </button>
        </div>
      </div>
      <div v-else class="loading-state">
        <p>正在加载题目...</p>
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
const questions = ref([])
const answers = ref([])
const currentIndex = ref(0)
const loading = ref(true)

const currentQuestion = computed(() => questions.value[currentIndex.value])

const isAnswered = (index) => {
  return answers.value[index] && answers.value[index].trim().length > 0
}

onMounted(() => {
  const storedQuestions = sessionStorage.getItem('interviewQuestions')
  if (storedQuestions) {
    try {
      questions.value = JSON.parse(storedQuestions)
      answers.value = new Array(questions.value.length).fill('')
    } catch (e) {
      console.error('Failed to parse questions', e)
    }
  }

  if (questions.value.length === 0) {
    // If no questions, maybe redirect back to config or load from API
    // Try fetch from API if session storage empty (e.g. refresh)
    // For now redirect
    alert('未找到题目，请重新配置')
    router.push('/config')
  }
  loading.value = false
})

const jumpTo = (index) => {
  // Optional: save logic or validation
  currentIndex.value = index
}

const prevQuestion = () => {
  if (currentIndex.value > 0) currentIndex.value--
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) currentIndex.value++
}

const submitAll = async () => {
  const confirmSubmit = confirm('确定要提交所有回答吗？提交后将无法修改。')
  if (!confirmSubmit) return

  try {
    const sessionId = route.query.sessionId
    const payload = {
      sessionId: sessionId,
      answers: answers.value.map((ans, idx) => ({
        questionId: questions.value[idx].id,
        answer: ans
      }))
    }

    // Using axios for submission
    // URL might be /api/interview/submit or /api/interview/evaluate
    // Based on user context, likely /api/interview/result logic handles evaluation or separate endpoint
    // Assuming backend endpoint /api/submit or similar for Vue
    const res = await axios.post('/api/interview/submit', payload)

    if (res.data.success || res.status === 200) {
      router.push({ path: '/result', query: { sessionId } })
    }
  } catch (err) {
    console.error('Submission failed', err)
    alert('提交失败，请重试')
  }
}
</script>

<style scoped>
.interview-container {
  display: flex;
  height: 100vh;
  background-color: #f7f9fc;
}

.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
}

.sidebar h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  color: #333;
}

.question-list {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
}

.question-list li {
  padding: 0.75rem 1rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #555;
  font-size: 0.95rem;
  transition: background 0.2s;
}

.question-list li:hover {
  background-color: #f5f5f5;
}

.question-list li.active {
  background-color: #e6f7ff; /* Light blue */
  color: #1890ff; /* Blue */
  font-weight: 600;
}

.question-list li.completed .status-dot {
  background-color: #52c41a; /* Green */
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #d9d9d9; /* Grey */
  margin-right: 10px;
}

.btn-submit-all {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #ff4d4f; /* Red */
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
}

.btn-submit-all:hover {
  background: #ff7875;
}

.main-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  display: flex;
  justify-content: center;
}

.question-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  height: fit-content;
  min-height: 500px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 1rem;
}

.question-number {
  font-size: 1.1rem;
  font-weight: bold;
  color: #667eea;
}

.question-type {
  background: #f0f2f5;
  color: #666;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
}

.question-body {
  margin-bottom: 2rem;
}

.question-text {
  font-size: 1.1rem;
  line-height: 1.6;
  white-space: pre-wrap;
}

.answer-area textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  min-height: 150px;
}

.answer-area textarea:focus {
  border-color: #667eea;
  outline: none;
}

.card-footer {
  margin-top: auto;
  padding-top: 2rem;
  display: flex;
  justify-content: space-between;
}

.btn-nav {
  padding: 0.6rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-prev {
  background: white;
  border: 1px solid #d9d9d9;
  color: #666;
}

.btn-prev:hover:not(:disabled) {
  border-color: #667eea;
  color: #667eea;
}

.btn-prev:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-next {
  background: #667eea;
  color: white;
  border: none;
}

.btn-next:hover {
  background: #5a6fd1;
}

.btn-submit {
  background: #52c41a; /* Green */
  color: white;
  border: none;
}

.btn-submit:hover {
  background: #73d13d;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #888;
}
</style>

