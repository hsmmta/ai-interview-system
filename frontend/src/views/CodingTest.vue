<template>
  <div class="coding-test">
    <h2>编程测试环节 (共3题)</h2>
    <div v-if="!finished">
      <div class="question-header">
        <span class="q-num">第 {{ currentQuestionIndex + 1 }} 题 / 共 3 题</span>
        <span class="q-type" v-if="currentQuestionIndex === 0">[代码找错(Debug)] 限时</span>
        <span class="q-type" v-else-if="currentQuestionIndex === 1">[基础编程] 限时</span>
        <span class="q-type" v-else>[进阶编程] 综合抗压能力测试</span>
        <span class="q-timer" v-if="currentQuestionIndex < 2">剩余时间: <span class="time">{{ formattedTime }}</span></span>
      </div>
      <div class="question-content">
        <pre class="question-text">{{ questions[currentQuestionIndex].text }}</pre>
      </div>

      <div class="editor-header">
        <label>选择编程语言: </label>
        <select v-model="selectedLanguage" class="lang-select">
          <option value="text">纯文本</option>
          <option value="python">Python</option>
          <option value="java">Java</option>
          <option value="cpp">C++</option>
          <option value="javascript">JavaScript</option>
        </select>
      </div>

      <div class="editor-area">
        <codemirror
          v-model="answers[currentQuestionIndex]"
          :style="{ height: '400px', border: '1px solid #ddd', borderRadius: '8px' }"
          :autofocus="true"
          :indent-with-tab="true"
          :tab-size="4"
          :extensions="extensions"
        />
      </div>

      <div class="actions">
        <button class="btn btn-primary" @click="nextQuestion">
          {{ currentQuestionIndex < 2 ? '下一题' : '完成并提交评估' }}
        </button>
      </div>
    </div>
    <div v-else class="loading-state">
      <p>正在生成综合评估报告，请耐心等待...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { Codemirror } from 'vue-codemirror'
import { basicSetup } from 'codemirror'
import { python } from '@codemirror/lang-python'
import { java } from '@codemirror/lang-java'
import { cpp } from '@codemirror/lang-cpp'
import { javascript } from '@codemirror/lang-javascript'

const router = useRouter()
const route = useRoute()

const questions = ref([
  { id: 1, text: "题目1：请找出一小段 Python 代码中的逻辑/语法错误并修正。\n\ndef fibonacci(n):\n    if n = 0:\n        return 0\n    elif n == 1\n        return 1\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)" },
  { id: 2, text: "题目2：实现一个简单的 LRU (Least Recently Used) 缓存策略类（只要求基本功能结构即可）。" },
  { id: 3, text: "题目3：进阶题：请使用你熟悉的语言，描述并写出一段能处理并发任务控制（例如限制最大并发数为10的请求函数）的代码逻辑或伪代码。" }
])

const answers = ref(['', '', ''])
const currentQuestionIndex = ref(0)
const finished = ref(false)
const selectedLanguage = ref('python')

const timeLeft = ref(600)
let timer = null

const startTimer = () => {
  clearInterval(timer)
  if (currentQuestionIndex.value < 2) {
    timeLeft.value = 600 // 10 minutes
    timer = setInterval(() => {
      if (timeLeft.value > 0) {
        timeLeft.value--
      } else {
        clearInterval(timer)
        alert('时间到，将自动提交或进入下一题！')
        nextQuestion()
      }
    }, 1000)
  }
}

const formattedTime = computed(() => {
  const m = Math.floor(timeLeft.value / 60)
  const s = timeLeft.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

onMounted(() => {
  startTimer()
})

onUnmounted(() => {
  clearInterval(timer)
})

const extensions = computed(() => {
  const exts = [basicSetup]
  if (selectedLanguage.value === 'python') {
    exts.push(python())
  } else if (selectedLanguage.value === 'java') {
    exts.push(java())
  } else if (selectedLanguage.value === 'cpp') {
    exts.push(cpp())
  } else if (selectedLanguage.value === 'javascript') {
    exts.push(javascript())
  }
  return exts
})

const userInfo = JSON.parse(sessionStorage.getItem('userInfo') || '{}')
const interviewSession = JSON.parse(sessionStorage.getItem('interviewAnswers') || '[]')

const nextQuestion = async () => {
  clearInterval(timer)
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
    startTimer()
  } else {
    // 提交处理
    finished.value = true

    try {
      // 整理编码题结果 (mock)
      const codingResults = {
         q1: answers.value[0],
         q2: answers.value[1],
         q3: answers.value[2],
      }

      const payload = {
        session_id: route.query.sessionId,
        user_info: `应聘岗位：${sessionStorage.getItem('postPosition')}，简历内容：${sessionStorage.getItem('resumeText')}`,
        user_answers: interviewSession,
        coding_results: codingResults
      }

      console.log('提交最终评估:', payload)

      const response = await axios.post('/api/fastapi/interview/interactive/evaluate', payload)

      if (response.data && response.data.status === 'success') {
        const reportDataObj = {
          report: response.data.data.realtime_evaluation || response.data.data.evaluationText || response.data.data,
          history: response.data.data.history || interviewSession,
          coding: codingResults,
          codingQuestions: questions.value.map(q => q.text)
        }

        // 解析 report 提取出培养方案 (如果后端是一起返回的)
        if (typeof reportDataObj.report === 'string') {
          const reportText = reportDataObj.report
          const trainingIndex = reportText.indexOf('【培养方案】')
          if (trainingIndex !== -1) {
             reportDataObj.training_program = reportText.slice(trainingIndex).replace('【培养方案】', '').trim()
             reportDataObj.report = reportText.slice(0, trainingIndex).trim()
          }
        }

        sessionStorage.setItem('evaluationReport', JSON.stringify(reportDataObj))
        router.push('/result?sessionId=' + (route.query.sessionId || ''))
      } else {
        alert('评估生成失败')
        finished.value = false
      }
    } catch (error) {
      console.error(error)
      alert('网络异常，生成评估失败')
      finished.value = false
    }
  }
}
</script>

<style scoped>
.coding-test {
  max-width: 900px;
  margin: 40px auto;
  padding: 30px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.question-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  font-weight: bold;
}
.q-num {
  color: #333;
}
.q-type {
  color: #ff6b6b;
}
.q-timer {
  font-size: 16px;
  color: #ff4d4f;
  font-weight: bold;
}
.q-timer .time {
  display: inline-block;
  min-width: 50px;
  text-align: right;
}
.question-content {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.question-text {
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 16px;
  line-height: 1.5;
}
.editor-header {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}
.lang-select {
  padding: 5px 10px;
  font-size: 14px;
  border-radius: 4px;
  border: 1px solid #ccc;
  margin-left: 10px;
  outline: none;
}
.editor-area {
  margin-bottom: 20px;
}
.actions {
  margin-top: 20px;
  text-align: right;
}
.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
}
.btn-primary {
  background: #1890ff;
  color: #fff;
}
.btn-primary:hover {
  background: #0f7ae5;
}
.loading-state {
  text-align: center;
  padding: 50px;
  font-size: 18px;
  color: #666;
}
</style>
