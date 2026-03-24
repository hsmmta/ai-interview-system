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
          <div class="header-left">
            <span class="question-number">{{ currentIndex + 1 }}/{{ questions.length }}</span>
            <span class="question-type">{{ currentQuestion.type === 'coding' ? '编程题' : '简答题' }}</span>
          </div>
        </div>

        <div class="question-body">
          <!-- Context/Main Body -->
          <div v-if="parsedContent.context" class="q-context">
            {{ parsedContent.context }}
          </div>

          <!-- Sub Questions -->
          <div v-for="(subQ, idx) in parsedContent.subs" :key="idx" class="sub-q-item">
            <div class="sub-q-label" v-if="parsedContent.subs.length > 1">
              问题 {{ idx + 1 }}: {{ subQ }}
            </div>
            <div class="sub-q-label" v-else>
              {{ subQ }}
            </div>

            <textarea
              v-model="currentSubAnswers[idx]"
              class="sub-answer-box"
              :placeholder="parsedContent.subs.length > 1 ? `请输入问题 ${idx + 1} 的回复...` : '请输入你的回答...'"
              @input="syncAnswer"
              rows="6"
            ></textarea>
          </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const questions = ref([])
const answers = ref([])
const currentIndex = ref(0)
const loading = ref(true)

// Stores parsing state for each question to avoid re-parsing
const questionStates = ref({})

const currentQuestion = computed(() => questions.value[currentIndex.value])

const parsedContent = computed(() => {
  if (!currentQuestion.value) return { context: '', subs: [] }
  return getParsedState(currentIndex.value).parsed
})

const currentSubAnswers = computed(() => {
  return getParsedState(currentIndex.value).subAnswers
})

// Logic adapted from JSP parseQuestionContent
const parseQuestionContent = (content) => {
  if (!content) return { context: "", subs: [] };
  // Check for structure
  if (!content.includes("\n") || !/-\s/.test(content)) {
       return { context: "", subs: [content] };
  }

  const lines = content.split('\n');
  let contextLines = [];
  let subs = [];
  let foundFirstBullet = false;

  lines.forEach(line => {
      const trimmed = line.trim();
      // Match "- " or "- 追问" start
      if (trimmed.startsWith("-")) {
          foundFirstBullet = true;
          // Clean prefixes
          let clean = trimmed.replace(/^-\s*(追问\d*[：:]?)?\s*/, '');
          subs.push(clean);
      } else {
          if (!foundFirstBullet) {
              contextLines.push(line);
          } else {
              if (subs.length > 0) {
                  subs[subs.length - 1] += "\n" + line;
              } else {
                  contextLines.push(line);
              }
          }
      }
  });

  return {
      context: contextLines.join('\n').trim(),
      subs: subs.length > 0 ? subs : [content]
  };
}

const getParsedState = (index) => {
  if (!questionStates.value[index]) {
    const q = questions.value[index]
    const parsed = parseQuestionContent(q.question || q.content)
    // Initialize subAnswers from existing answer if possible, or empty
    // If we are reloading answers from storage, we might need logic to split them back?
    // For now assuming empty or flat string.
    // Let's keep it simple: empty array
    let initialSubs = new Array(parsed.subs.length).fill('')

    // Attempt to restore if already answered (simple restore)
    if (answers.value[index]) {
       // Heuristic: If we joined by \n---\n, split by it?
       // For now, if single string exists, put it in first box
       initialSubs[0] = answers.value[index]
    }

    questionStates.value[index] = {
      parsed: parsed,
      subAnswers: initialSubs
    }
  }
  return questionStates.value[index]
}

const syncAnswer = () => {
  const state = getParsedState(currentIndex.value)
  // Join sub-answers to form single string for storage/submission
  // Using a distinct separator to possibly reconstruct later if needed
  answers.value[currentIndex.value] = state.subAnswers.join('\n\n')
}

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
    alert('未找到题目，请重新配置')
    router.push('/config')
  }
  loading.value = false
})

const jumpTo = (index) => {
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
  background-color: #e6f7ff;
  color: #1890ff;
  font-weight: 600;
}

.question-list li.completed .status-dot {
  background-color: #52c41a;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #d9d9d9;
  margin-right: 10px;
}

.btn-submit-all {
  margin-top: 1rem;
  padding: 0.75rem;
  background: #ff4d4f;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
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

.q-context {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  line-height: 1.6;
  color: #333;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 6px;
  border-left: 4px solid #667eea;
}

.sub-q-item {
  margin-bottom: 2rem;
}

.sub-q-label {
  font-weight: 600;
  color: #444;
  margin-bottom: 0.8rem;
  font-size: 1rem;
}

.sub-answer-box {
  width: 100%;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  min-height: 100px;
  background: #fff;
  transition: border-color 0.2s;
}

.sub-answer-box:focus {
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

.btn-next {
  background: #667eea;
  color: white;
  border: none;
}

.btn-submit {
  background: #52c41a;
  color: white;
  border: none;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #888;
}
</style>
