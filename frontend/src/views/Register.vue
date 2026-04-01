<template>
  <div class="register-container">
    <div class="register-card">
      <h2>新用户注册</h2>
      <p class="subtitle">加入最好的 AI 面试平台</p>

      <form @submit.prevent="handleRegister">

        <div class="form-group">
          <label>姓名</label>
          <input
            v-model="name"
            type="text"
            placeholder="请输入姓名"
            required
          />
        </div>

        <div class="form-group">
          <label>邮箱</label>
          <input
            v-model="email"
            type="email"
            placeholder="请输入邮箱"
            required
          />
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

        <div class="form-group">
          <label>密码</label>
          <input
            v-model="password"
            type="password"
            placeholder="请输入密码（不少于6位）"
            required
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label>确认密码</label>
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label>验证码</label>
          <div class="verify-group">
            <input
              v-model="code"
              type="text"
              placeholder="4位验证码"
              maxlength="4"
              required
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


        <div v-if="error" class="error-msg">{{ error }}</div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? '注册中...' : '立即注册' }}
        </button>

        <div class="actions">
          <router-link to="/login">已有账号？去登录</router-link>
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
const name = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const code = ref('')
const cooldown = ref(0)
const loading = ref(false)
const error = ref('')

const isValidPhone = computed(() => /^1[3-9]\d{9}$/.test(phone.value))

const sendCode = async () => {
  if (!isValidPhone.value) return

  try {
    // Send request to send verification code
    const res = await axios.post('/api/register', { action: 'sendCode', phone: phone.value })
    if (res.data.success === false) {
      error.value = res.data.message || '发送失败'
      return
    }

    cooldown.value = 60
    const timer = setInterval(() => {
      cooldown.value--
      if (cooldown.value <= 0) clearInterval(timer)
    }, 1000)

  } catch (err) {
    if (err.response && err.response.data) {
       error.value = err.response.data.error || err.response.data.message || '操作失败'
    } else {
       error.value = '发送失败，请稍后重试'
    }
  }
}

const handleRegister = async () => {
  loading.value = true
  error.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    loading.value = false
    return
  }

  try {
    const res = await axios.post('/api/register', {
      action: 'register',
      name: name.value,
      email: email.value,
      phone: phone.value,
      password: password.value,
      code: code.value
    })

    if (res.data.success || res.status === 200) {
      if (res.request.responseURL.includes('/login') || res.request.responseURL.includes('/profile')) {
          router.push('/login')
      } else {
          // Assume success
          router.push('/login')
      }
    } else {
      error.value = res.data.message || res.data.error || '注册失败'
    }
  } catch (err) {
    if (err.response && err.response.data) {
        error.value = err.response.data.error || err.response.data.message || '操作失败'
    } else {
        error.value = '注册请求失败'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 0;
}

.register-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 500px;
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

input[type="text"],
input[type="email"],
input[type="tel"],
input[type="password"] {
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
  min-width: 100px;
}

.btn-verify:not(:disabled):hover {
  background: #e6e8eb;
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

