<template>
  <div class="interview-voice-container">
    <div class="header">
      <div class="progress-info">
        <span>当前进度: {{ currentIndex + 1 }} / {{ questions.length }}</span>
        <div class="progress-bar">
          <div class="progress" :style="{ width: ((currentIndex + 1) / questions.length) * 100 + '%' }"></div>
        </div>
      </div>
      <button class="btn-submit-all" @click="submitAll">提交所有回答</button>
    </div>

    <div class="main-content">
      <div v-if="currentQuestion" class="question-card">
        <h3 class="question-title">第 {{ currentIndex + 1 }} 题</h3>
        <p class="question-text">{{ currentQuestion.question }}</p>

        <div class="answer-section">
          <div class="voice-controls">
            <button
              class="btn-record"
              :class="{ recording: isRecording }"
              @mousedown="startRecording"
              @mouseup="stopRecording"
              @touchstart.prevent="startRecording"
              @touchend.prevent="stopRecording"
            >
              <div class="icon-mic">🎤</div>
              <span>{{ isRecording ? '松开结束' : '按住说话' }}</span>
            </button>
            <span class="status-text">{{ statusText }}</span>
          </div>

          <textarea
            v-model="answers[currentIndex]"
            class="transcribed-text"
            placeholder="语音识别结果将显示在这里，您可以手动修改..."
            rows="6"
          ></textarea>
        </div>

        <div class="navigation">
          <button
            class="btn-nav btn-prev"
            :disabled="currentIndex === 0"
            @click="prevQuestion"
          >
            上一题
          </button>
          <button
            v-if="currentIndex < questions.length - 1"
            class="btn-nav btn-next"
            @click="nextQuestion"
          >
            下一题
          </button>
          <button
            v-else
            class="btn-nav btn-finish"
            @click="submitAll"
          >
            完成面试
          </button>
        </div>
      </div>
      <div v-else class="loading">加载题目中...</div>
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
const isRecording = ref(false)
const statusText = ref('准备就绪')
const mediaRecorder = ref(null)
const audioChunks = ref([])

const currentQuestion = computed(() => questions.value[currentIndex.value])

onMounted(() => {
  const storedQuestions = sessionStorage.getItem('interviewQuestions')
  if (storedQuestions) {
    questions.value = JSON.parse(storedQuestions)
    answers.value = new Array(questions.value.length).fill('')
  } else {
    // Fallback or redirect
    alert('未找到题目')
    router.push('/config')
  }
})

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream) // Using default mimeType or handle compat
    audioChunks.value = []

    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
    }

    mediaRecorder.value.onstop = async () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' }) // adjust type if needed
      await processAudio(audioBlob)
    }

    mediaRecorder.value.start()
    isRecording.value = true
    statusText.value = '正在录音...'
  } catch (err) {
    console.error('Microphone access denied', err)
    statusText.value = '无法访问麦克风'
  }
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    statusText.value = '正在识别...'

    // Stop tracks
    mediaRecorder.value.stream.getTracks().forEach(track => track.stop())
  }
}

const processAudio = async (audioBlob) => {
  const formData = new FormData()
  // Add sessionId to filename if needed by backend
  const filename = `audio_${route.query.sessionId}_${currentIndex.value}.webm`
  formData.append('audio_file', audioBlob, filename) // Key matches SenseVoice API expectance?
  formData.append('language', 'auto') // if needed

  try {
    // Call backend proxy which forwards to SenseVoice API or handles it
    // Assuming /api/analyze-interview exists or similar
    const res = await axios.post('/api/analyze-interview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (res.data.code === 200 && res.data.data && res.data.data.candidate_text) {
      const text = res.data.data.candidate_text
      // Append or replace?
      if (answers.value[currentIndex.value]) {
        answers.value[currentIndex.value] += ' ' + text
      } else {
        answers.value[currentIndex.value] = text
      }
      statusText.value = '识别成功'
    } else {
      statusText.value = '识别失败: ' + (res.data.msg || '未知错误')
    }
  } catch (err) {
    console.error('Audio upload failed', err)
    statusText.value = '上传失败'
  }
}

const prevQuestion = () => {
  if (currentIndex.value > 0) currentIndex.value--
}

const nextQuestion = () => {
  if (currentIndex.value < questions.value.length - 1) currentIndex.value++
}

const submitAll = async () => {
  if (!confirm('确定提交所有回答吗？')) return

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
    console.error('Submit failed', err)
    alert('提交失败')
  }
}
</script>

<style scoped>
.interview-voice-container {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.progress-info {
  flex: 1;
  max-width: 400px;
}

.progress-bar {
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 5px;
}

.progress {
  height: 100%;
  background: #667eea;
  transition: width 0.3s ease;
}

.btn-submit-all {
  padding: 0.5rem 1rem;
  background: #ff4d4f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.main-content {
  flex: 1;
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.question-card {
  background: white;
  width: 100%;
  max-width: 600px;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.question-title {
  color: #667eea;
  margin-top: 0;
}

.question-text {
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.voice-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1.5rem;
}

.btn-record {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: white;
  border: 4px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
  user-select: none;
}

.btn-record:active, .btn-record.recording {
  background: #667eea;
  border-color: #e0e7ff;
  color: white;
  transform: scale(0.95);
}

.icon-mic {
  font-size: 1.5rem;
  margin-bottom: 4px;
}

.status-text {
  margin-top: 1rem;
  color: #888;
  font-size: 0.9rem;
}

.transcribed-text {
  width: 100%;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  background: #fafafa;
}

.navigation {
  margin-top: 2rem;
  display: flex;
  justify-content: space-between;
}

.btn-nav {
  padding: 0.75rem 2rem;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
}

.btn-prev {
  background: white;
  border: 1px solid #ddd;
  color: #666;
}

.btn-next {
  background: #667eea;
  color: white;
  border: none;
}

.btn-finish {
  background: #52c41a;
  color: white;
  border: none;
}
</style>

