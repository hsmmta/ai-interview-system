<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>用户注册 - AI 模拟面试平台</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .register-container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        h2 { text-align: center; color: #333; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #666; font-weight: 500; }
        input[type="text"], input[type="password"], input[type="email"], input[type="tel"] { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; font-size: 14px; transition: border-color 0.3s; }
        input:focus { border-color: #007bff; outline: none; }
        .code-group { display: flex; gap: 10px; }
        .code-group input { flex: 1; }
        .btn-code { background-color: #6c757d; color: white; border: none; padding: 0 15px; border-radius: 6px; cursor: pointer; font-size: 13px; white-space: nowrap; }
        .btn-code:hover { background-color: #5a6268; }
        .btn-primary { width: 100%; background-color: #007bff; color: white; border: none; padding: 14px; border-radius: 6px; font-size: 16px; cursor: pointer; font-weight: 600; transition: background-color 0.3s; }
        .btn-primary:hover { background-color: #0056b3; }
        .links { margin-top: 20px; text-align: center; font-size: 14px; }
        .links a { color: #007bff; text-decoration: none; }
        .links a:hover { text-decoration: underline; }
        #message { margin-top: 15px; text-align: center; color: #dc3545; font-size: 14px; min-height: 20px;}
    </style>
</head>
<body>
<div class="register-container">
    <h2>注册新账号</h2>
    <div class="form-group">
        <label>手机号</label>
        <input type="tel" id="phone" placeholder="请输入手机号">
    </div>
    <div class="form-group code-group">
        <input type="text" id="code" placeholder="短信验证码">
        <button class="btn-code" onclick="sendCode(this)">获取验证码</button>
    </div>
    <div class="form-group">
        <label>姓名</label>
        <input type="text" id="name" placeholder="请输入真实姓名">
    </div>
    <div class="form-group">
        <label>电子邮箱</label>
        <input type="email" id="email" placeholder="请输入邮箱地址">
    </div>
    <div class="form-group">
        <label>密码</label>
        <input type="password" id="password" placeholder="请输入密码">
    </div>
    <div class="form-group">
        <label>确认密码</label>
        <input type="password" id="confirmPassword" placeholder="请再次输入密码">
    </div>
    <div class="form-group">
        <label>意向岗位</label>
        <select id="targetPosition" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; box-sizing: border-box; font-size: 14px; background: white; appearance: none; -webkit-appearance: none;">
            <option value="ai算法工程师">ai算法工程师</option>
            <option value="ai数据开发工程师">ai数据开发工程师</option>
        </select>
    </div>
    <div id="message"></div>
    <button class="btn-primary" onclick="doRegister()">立即注册</button>
    <div class="links">
        已有账号？<a href="login.jsp">直接登录</a>
    </div>
</div>

<script>
    async function sendCode(btn) {
        const phone = document.getElementById('phone').value.trim();
        if(!phone) return showMsg('请输入手机号');

        btn.disabled = true;
        let sec = 60;
        const timer = setInterval(() => {
            btn.innerText = sec + "s后重试";
            sec--;
            if(sec < 0) {
                clearInterval(timer);
                btn.disabled = false;
                btn.innerText = '获取验证码';
            }
        }, 1000);

        try {
            const res = await fetch('api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action: 'sendCode', phone })
            });
            const data = await res.json();
            if(data.success) {
                showMsg('验证码已发送', '#28a745');
                if(data.devCode) console.log('DevCode:', data.devCode);
            } else {
                showMsg(data.message || '发送失败');
                clearInterval(timer);
                btn.disabled = false;
                btn.innerText = '获取验证码';
            }
        } catch(e) {
            showMsg('网络错误');
            clearInterval(timer);
            btn.disabled = false;
            btn.innerText = '获取验证码';
        }
    }

    async function doRegister() {
        const phone = document.getElementById('phone').value.trim();
        const code = document.getElementById('code').value.trim();
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();
        const confirmPassword = document.getElementById('confirmPassword').value.trim();
        const targetPosition = document.getElementById('targetPosition').value.trim();

        if(!phone || !code || !name || !password) return showMsg('请填写必要信息');
        if(password !== confirmPassword) return showMsg('两次输入密码不一致');

        try {
            const res = await fetch('api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ action: 'register', phone, code, name, email, password, targetPosition })
            });
            const data = await res.json();
            if(data.success) {
                showMsg('注册成功，正在跳转...', '#28a745');
                setTimeout(() => location.href = 'profile.jsp', 1500);
            } else {
                showMsg(data.message);
            }
        } catch(e) {
            showMsg('注册失败：' + e.message);
        }
    }

    function showMsg(text, color='#dc3545') {
        const el = document.getElementById('message');
        el.style.color = color;
        el.innerText = text;
    }
</script>
</body>
</html>

