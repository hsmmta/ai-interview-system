<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>登录 - AI 模拟面试平台</title>
    <style>
        :root {
            --primary-color: #4A90E2;
            --primary-hover: #357ABD;
            --bg-color: #F4F7F6;
            --text-color: #333;
            --text-secondary: #666;
            --card-radius: 12px;
            --shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg-color);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background-image: radial-gradient(#e0e0e0 1px, transparent 1px);
            background-size: 20px 20px;
        }
        .login-box {
            background: white;
            border-radius: var(--card-radius);
            padding: 48px;
            width: 90%;
            max-width: 420px;
            box-shadow: var(--shadow);
            transition: transform 0.3s ease;
        }
        .login-box:hover {
            transform: translateY(-5px);
        }
        h1 {
            text-align: center;
            margin-bottom: 8px;
            color: var(--text-color);
            font-size: 28px;
            font-weight: 700;
        }
        .subtitle {
            text-align: center;
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 40px;
        }
        .input-group { margin-bottom: 24px; position: relative; }
        label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-color);
            font-size: 14px;
            font-weight: 500;
        }
        input {
            width: 100%;
            padding: 14px 16px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 15px;
            transition: all 0.3s;
            background: #fafafa;
        }
        input:focus {
            outline: none;
            border-color: var(--primary-color);
            background: white;
            box-shadow: 0 0 0 4px rgba(74, 144, 226, 0.1);
        }
        .code-row { display: flex; gap: 12px; }
        .code-row input { flex: 1; }
        .code-row button {
            width: 130px;
            background: #e8f0fe;
            color: var(--primary-color);
            font-weight: 600;
        }
        .code-row button:hover {
            background: #d0e1fd;
            color: var(--primary-hover);
        }
        button {
            width: 100%;
            padding: 14px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.3s;
            letter-spacing: 0.5px;
        }
        button:hover {
            background: var(--primary-hover);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            box-shadow: none;
        }
        .error {
            color: #d9534f;
            font-size: 13px;
            margin-top: 16px;
            text-align: center;
            background: #fff5f5;
            padding: 8px;
            border-radius: 6px;
        }
        .success {
            color: #2e7d32;
            font-size: 13px;
            margin-top: 16px;
            text-align: center;
            background: #e8f5e9;
            padding: 8px;
            border-radius: 6px;
        }
    </style>
</head>
<body>
<div class="login-box">
    <h1>AI 模拟面试平台</h1>
    <p class="subtitle">更智能的面试准备助手</p>

    <div class="input-group">
        <label>手机号码</label>
        <input type="tel" id="phone" placeholder="请输入11位手机号" maxlength="11" />
    </div>
    <div class="input-group">
        <label>验证码</label>
        <div class="code-row">
            <input type="text" id="code" placeholder="6位数字" maxlength="6" />
            <button id="sendCodeBtn">获取验证码</button>
        </div>
    </div>
    <button id="loginBtn">立即登录</button>
    <div style="text-align:center; margin-top:15px; font-size:14px;">
        <a href="<%= request.getContextPath() %>/register.jsp" style="color:#4a90e2; text-decoration:none;">注册新账号</a>
    </div>
    <div id="message"></div>
</div>

<script>
    const phoneInput = document.getElementById("phone");
    const codeInput = document.getElementById("code");
    const sendCodeBtn = document.getElementById("sendCodeBtn");
    const loginBtn = document.getElementById("loginBtn");
    const message = document.getElementById("message");

    // Build API base path safely for both ROOT and non-ROOT deployment.
    const ctx = "<%= request.getContextPath() %>";
    const base = ctx && ctx !== "/" ? ctx : "";
    const loginApi = base + "/api/login";

    let countdown = 0;

    sendCodeBtn.addEventListener("click", async () => {
        const phone = phoneInput.value.trim();
        if (!/^1[3-9]\d{9}$/.test(phone)) {
            showMessage("请输入正确的手机号", "error");
            return;
        }

        try {
            const res = await fetch(loginApi, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({action: "sendCode", phone})
            });

            const data = await res.json();
            if (res.ok) {
                showMessage("验证码已发送（开发模式：" + (data.devCode || "") + "）", "success");
                startCountdown();
            } else {
                showMessage(data.error || "发送失败", "error");
            }
        } catch (e) {
            showMessage("网络错误", "error");
        }
    });

    loginBtn.addEventListener("click", async () => {
        const phone = phoneInput.value.trim();
        const code = codeInput.value.trim();

        if (!phone || !code) {
            showMessage("请填写完整信息", "error");
            return;
        }

        try {
            const res = await fetch(loginApi, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({action: "verify", phone, code})
            });

            const data = await res.json();
            if (res.ok) {
                showMessage("登录成功，跳转中...", "success");
                setTimeout(() => {
                    window.location.href = base + "/profile.jsp";
                }, 1000);
            } else {
                showMessage(data.error || "登录失败", "error");
            }
        } catch (e) {
            showMessage("网络错误", "error");
        }
    });

    function startCountdown() {
        countdown = 60;
        sendCodeBtn.disabled = true;
        const timer = setInterval(() => {
            countdown--;
            sendCodeBtn.textContent = countdown + "秒后重试";
            if (countdown <= 0) {
                clearInterval(timer);
                sendCodeBtn.disabled = false;
                sendCodeBtn.textContent = "获取验证码";
            }
        }, 1000);
    }

    function showMessage(text, type) {
        message.textContent = text;
        message.className = type;
    }
</script>
</body>
</html>

