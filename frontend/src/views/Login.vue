<template>
  <div class="login-container">
    <div class="login-card">
      <h2>AI 模拟面试平台</h2>
      <p class="subtitle">让面试准备更高效、更智能</p>

      <form @submit.prevent="handleLogin">
        <div class="login-tabs">
          <span :class="{ active: loginType === 'password' }" @click="loginType = 'password'">密码登录</span>
          <span :class="{ active: loginType === 'code' }" @click="loginType = 'code'">验证码登录</span>
        </div>

        <div class="form-group">
          <label>手机号码</label>
          <div class="input-group">
            <span class="prefix">+86</span>
            <input
              v-model="phone"
              type="tel"
              placeholder="请输入手机号"
              maxlength="11"
              required
            />
          </div>
        </div>

        <div v-if="loginType === 'code'" class="form-group">
          <label>验证码</label>
          <div class="verify-group">
            <input
              v-model="code"
              type="text"
              placeholder="4位验证码"
              maxlength="4"
              :required="loginType === 'code'"
            />
            <button
              type="button"
              class="btn-verify"
              :disabled="cooldown > 0 || !isValidPhone"
              @click="sendCode"
            >
              {{ cooldown > 0 ? `${cooldown}s` : '获取验证码' }}
            </button>
          </div>
        </div>

        <div v-else class="form-group">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            :required="loginType === 'password'"
          />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? '登录中...' : '立即登录' }}
        </button>

        <div class="actions">
          <router-link to="/register">没有账号？去注册</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const phone = ref('')
const code = ref('')
const password = ref('')
const loginType = ref('password')
const cooldown = ref(0)
const loading = ref(false)
const error = ref('')

const isValidPhone = computed(() => /^1[3-9]\d{9}$/.test(phone.value))

const sendCode = async () => {
  if (!isValidPhone.value) return

  try {
    const res = await axios.post('/api/login', { action: 'sendCode', phone: phone.value })

    if (res.data && res.data.success === false) {
      error.value = res.data.message || '发送失败'
      return
    }

    // Start cooldown
    cooldown.value = 60
    const timer = setInterval(() => {
      cooldown.value--
      if (cooldown.value <= 0) clearInterval(timer)
    }, 1000)

  } catch (err) {
    if (err.response && err.response.data) {
       error.value = err.response.data.error || err.response.data.message || '操作失败，请重试'
    } else {
       error.value = '请求失败，请稍后重试'
    }
    console.error(err)
  }
}

const handleLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const payload = { action: 'verify', phone: phone.value, loginType: loginType.value }
    if (loginType.value === 'code') {
      payload.code = code.value
    } else {
      payload.password = password.value
    }

    const res = await axios.post('/api/login', payload)

    if (res.data.success || res.status === 200) {
      // Assuming successful login sets a cookie or returns a token
      // For JSP backend, session cookie is likely used.
      if (res.request.responseURL.includes('/profile')) {
         router.push('/profile')
      } else {
         // Fallback if backend redirects via Location header which axios follows
         // If axios follows redirect, we might end up with profile page content in res.data
         // Better to check response
         router.push('/profile')
      }
    } else {
      error.value = res.data.message || res.data.error || '登录失败'
    }
  } catch (err) {
    if (err.response && err.response.data) {
        error.value = err.response.data.error || err.response.data.message || '登录请求失败'
    } else {
        error.value = '登录请求失败'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #444;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

input:focus {
  border-color: #667eea;
  outline: none;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
}

.prefix {
  position: absolute;
  left: 0.75rem;
  color: #666;
}

.input-group input {
  padding-left: 3rem;
}

.verify-group {
  display: flex;
  gap: 10px;
}

.btn-verify {
  white-space: nowrap;
  padding: 0 1rem;
  background: #f0f2f5;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  color: #666;
}

.btn-verify:not(:disabled):hover {
  background: #e6e8eb;
}

.login-tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.login-tabs span {
  padding: 10px 20px;
  cursor: pointer;
  color: #666;
  font-weight: 500;
  transition: all 0.3s;
  position: relative;
}

.login-tabs span.active {
  color: #667eea;
}

.login-tabs span.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #667eea;
}

.btn-submit {
  width: 100%;
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-submit:hover {
  background: #5a6fd1;
}

.actions {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.9rem;
}

.actions a {
  color: #667eea;
  text-decoration: none;
}

.error-msg {
  color: #ff4d4f;
  margin-bottom: 1rem;
  text-align: center;
  font-size: 0.9rem;
}
</style>
