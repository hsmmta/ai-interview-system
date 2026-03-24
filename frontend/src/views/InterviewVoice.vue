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
        <div class="voice-header">
          <h3 class="question-title">第 {{ currentIndex + 1 }} 题</h3>
        </div>

        <!-- Context Area -->
        <div v-if="parsedContent.context" class="q-context">
          {{ parsedContent.context }}
        </div>

        <!-- Sub Questions Area -->
        <div class="answer-section">
          <div v-for="(subQ, idx) in parsedContent.subs" :key="idx" class="sub-q-item">
            <div class="sub-q-label">
              {{ parsedContent.subs.length > 1 ? `问题 ${idx + 1}: ` : '' }}{{ subQ }}
            </div>

            <!-- Voice Controls for this sub-question -->
            <div class="voice-controls-inline">
              <button
                class="btn-record-sm"
                :class="{ recording: recordingIndex === idx }"
                @mousedown="startRecording(idx)"
                @mouseup="stopRecording(idx)"
                @touchstart.prevent="startRecording(idx)"
                @touchend.prevent="stopRecording(idx)"
              >
                <span v-if="recordingIndex === idx" class="icon-pulse">🔴</span>
                <span v-else>🎤</span>
              </button>

              <div class="status-inline">
                <span v-if="recordingIndex === idx">正在录音...</span>
                <span v-else-if="processingIndex === idx">正在识别...</span>
                <span v-else>按住说话</span>
              </div>
            </div>

            <textarea
              v-model="currentSubAnswers[idx]"
              class="transcribed-text"
              :placeholder="`语音识别结果将显示在这里 (${idx+1})...`"
              @input="syncAnswer"
              rows="4"
            ></textarea>
          </div>
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
const questionStates = ref({})

// Recording state
const recordingIndex = ref(-1) // -1 means none
const processingIndex = ref(-1)

// Audio Context State
let audioContext = null
let audioSource = null
let audioProcessor = null
let audioLeftChannel = []
let audioRecordingLength = 0
let audioSampleRate = 44100

const currentQuestion = computed(() => questions.value[currentIndex.value])

const parsedContent = computed(() => {
  if (!currentQuestion.value) return { context: '', subs: [] }
  return getParsedState(currentIndex.value).parsed
})

const currentSubAnswers = computed(() => {
  return getParsedState(currentIndex.value).subAnswers
})

// JSP-style Parser
const parseQuestionContent = (content) => {
  if (!content) return { context: "", subs: [] };
  if (!content.includes("\n") || !/-\s/.test(content)) {
       return { context: "", subs: [content] };
  }
  const lines = content.split('\n');
  let contextLines = [];
  let subs = [];
  let foundFirstBullet = false;
  lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith("-")) {
          foundFirstBullet = true;
          let clean = trimmed.replace(/^-\s*(追问\d*[：:]?)?\s*/, '');
          subs.push(clean);
      } else {
          if (!foundFirstBullet) {
              contextLines.push(line);
          } else {
              if (subs.length > 0) subs[subs.length - 1] += "\n" + line;
              else contextLines.push(line);
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
    let initialSubs = new Array(parsed.subs.length).fill('')
    if (answers.value[index]) {
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
  answers.value[currentIndex.value] = state.subAnswers.join('\n\n')
}

onMounted(() => {
  const storedQuestions = sessionStorage.getItem('interviewQuestions')
  if (storedQuestions) {
    questions.value = JSON.parse(storedQuestions)
    answers.value = new Array(questions.value.length).fill('')
  } else {
    alert('未找到题目')
    router.push('/config')
  }
})

// === WAV Helpers ===
const writeString = (view, offset, string) => {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}

const floatTo16BitPCM = (output, offset, input) => {
  for (let i = 0; i < input.length; i++, offset += 2) {
    let s = Math.max(-1, Math.min(1, input[i]))
    output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
  }
}

const encodeWAV = (samples, sampleRate) => {
  const buffer = new ArrayBuffer(44 + samples.length * 2)
  const view = new DataView(buffer)
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + samples.length * 2, true)
  writeString(view, 8, 'WAVE')
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true)
  view.setUint16(22, 1, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeString(view, 36, 'data')
  view.setUint32(40, samples.length * 2, true)
  floatTo16BitPCM(view, 44, samples)
  return new Blob([view.buffer], { type: 'audio/wav' })
}

const mergeBuffers = (channelBuffer, recordingLength) => {
  const result = new Float32Array(recordingLength)
  let offset = 0
  for (let i = 0; i < channelBuffer.length; i++) {
    const buffer = channelBuffer[i]
    result.set(buffer, offset)
    offset += buffer.length
  }
  return result
}

const startRecording = async (subIndex) => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    audioContext = new (window.AudioContext || window.webkitAudioContext)()
    audioSampleRate = audioContext.sampleRate
    audioSource = audioContext.createMediaStreamSource(stream)
    audioProcessor = audioContext.createScriptProcessor(4096, 1, 1)

    audioLeftChannel = []
    audioRecordingLength = 0

    audioProcessor.onaudioprocess = (e) => {
      if (recordingIndex.value !== subIndex) return
      const inputBuffer = e.inputBuffer.getChannelData(0)
      const bufferData = new Float32Array(inputBuffer)
      audioLeftChannel.push(bufferData)
      audioRecordingLength += bufferData.length
    }

    audioSource.connect(audioProcessor)
    audioProcessor.connect(audioContext.destination)

    recordingIndex.value = subIndex
  } catch (err) {
    console.error('Mic error', err)
    alert('无法访问麦克风')
  }
}

const stopRecording = (subIndex) => {
  if (recordingIndex.value === subIndex) {
    recordingIndex.value = -1
    processingIndex.value = subIndex

    // Cleanup audio context
    if (audioSource) {
       audioSource.mediaStream.getTracks().forEach(track => track.stop());
       audioSource.disconnect()
    }
    if (audioProcessor) {
      audioProcessor.disconnect()
      audioProcessor.onaudioprocess = null
    }

    if (audioRecordingLength > 0) {
        const pcmBuffer = mergeBuffers(audioLeftChannel, audioRecordingLength)
        const audioBlob = encodeWAV(pcmBuffer, audioSampleRate)
        processAudio(audioBlob, subIndex)
    } else {
        processingIndex.value = -1
    }
  }
}

const processAudio = async (audioBlob, subIndex) => {
  const formData = new FormData()
  const filename = `audio_${route.query.sessionId}_${currentIndex.value}_${subIndex}.wav`
  formData.append('audio_file', audioBlob, filename)
  formData.append('language', 'zh')

  try {
    const res = await axios.post('/api/analyze-interview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (res.data.code === 200 && res.data.data) {
      const text = res.data.data.candidate_text
      const state = getParsedState(currentIndex.value)
      // Append text
      const current = state.subAnswers[subIndex] || ''
      state.subAnswers[subIndex] = current + (current ? ' ' : '') + text
      syncAnswer()
    } else {
      alert('识别失败: ' + (res.data.msg || '未知错误'))
    }
  } catch (err) {
    console.error('Upload failed', err)
    alert('识别请求失败')
  } finally {
    processingIndex.value = -1
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
  max-width: 800px; /* Wider for voice layout */
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.voice-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 1rem;
}

.question-title {
  color: #667eea;
  margin: 0;
}

.q-context {
  margin-bottom: 2rem;
  font-size: 1.1rem;
  line-height: 1.6;
  color: #333;
  padding: 1.2rem;
  background: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.answer-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.sub-q-item {
  border: 1px solid #eee;
  padding: 1.5rem;
  border-radius: 8px;
}

.sub-q-label {
  font-weight: 600;
  color: #444;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.voice-controls-inline {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.btn-record-sm {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: white;
  border: 2px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.btn-record-sm:active, .btn-record-sm.recording {
  border-color: #ff4d4f;
  background: #fff1f0;
}

.icon-pulse {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}

.status-inline {
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
  font-family: inherit;
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
