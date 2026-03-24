<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个人中心 - AI 模拟面试平台</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; margin: 0; padding: 0; }
        .navbar { background: white; padding: 15px 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; }
        .navbar-brand { font-size: 20px; font-weight: bold; color: #333; }
        .navbar-user { display: flex; align-items: center; gap: 15px; }
        .btn-nav { text-decoration: none; color: #666; font-size: 14px; transition: color 0.2s; }
        .btn-nav:hover { color: #007bff; }
        .btn-logout { color: #dc3545; }

        .container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); padding: 30px; margin-bottom: 30px; }
        .card-header { font-size: 18px; font-weight: 600; color: #333; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }

        .info-row { display: flex; margin-bottom: 15px; align-items: center; }
        .info-label { width: 100px; color: #888; font-weight: 500; }
        .info-value { flex: 1; color: #333; font-size: 16px; }
        .info-input { flex: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px; display: none; }

        .btn-edit { background: #007bff; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-save { background: #28a745; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 14px; display: none; }
        .editing .info-value { display: none; }
        .editing .info-input { display: block; }
        .editing .btn-edit { display: none; }
        .editing .btn-save { display: inline-block; }

        .action-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .action-card { background: linear-gradient(135deg, #007bff 0%, #0062cc 100%); color: white; padding: 30px; border-radius: 12px; text-align: center; cursor: pointer; transition: transform 0.2s; text-decoration: none; }
        .action-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(0,123,255,0.3); }
        .action-card h3 { margin: 0 0 10px 0; font-size: 22px; }
        .action-card p { margin: 0; opacity: 0.9; font-size: 14px; }
        .action-card.secondary { background: white; color: #333; border: 1px solid #eee; }
        .action-card.secondary:hover { background: #f8f9fa; }
    </style>
</head>
<body>

<div class="navbar">
    <div class="navbar-brand">AI 模拟面试平台</div>
    <div class="navbar-user">
        <span id="nav-username">加载中...</span>
        <a href="login.jsp" class="btn-nav btn-logout">退出</a>
    </div>
</div>

<div class="container">
    <div class="card" id="profile-card">
        <div class="card-header">
            个人信息
            <button class="btn-edit" onclick="toggleEdit()">编辑</button>
            <button class="btn-save" onclick="saveProfile()">保存</button>
        </div>
        <div class="info-row">
            <span class="info-label">姓名</span>
            <span class="info-value" id="val-name"></span>
            <input type="text" class="info-input" id="in-name">
        </div>
        <div class="info-row">
            <span class="info-label">手机号</span>
            <span class="info-value" id="val-phone"></span>
            <input type="text" class="info-input" id="in-phone" disabled style="background:#f9f9f9; color:#999;" title="手机号不可修改">
        </div>
        <div class="info-row">
            <span class="info-label">邮箱</span>
            <span class="info-value" id="val-email"></span>
            <input type="email" class="info-input" id="in-email">
        </div>
        <div class="info-row">
            <span class="info-label">意向岗位</span>
            <span class="info-value" id="val-position"></span>
            <input type="text" class="info-input" id="in-position">
        </div>
    </div>

    <div class="action-cards">
        <a href="config.jsp" class="action-card">
            <h3>开始模拟面试</h3>
            <p>自定义方向、题量，全真模拟</p>
        </a>
        <a href="#" class="action-card secondary">
            <h3>历史记录</h3>
            <p>查看过往面试表现与评估（开发中）</p>
        </a>
    </div>
</div>

<script>
    let currentUser = {};

    async function loadProfile() {
        try {
            const res = await fetch('api/profile');
            if (res.status === 401) {
                location.href = 'login.jsp';
                return;
            }
            const data = await res.json();
            if (data.success) {
                currentUser = data.user;
                renderProfile();
            } else {
                alert('加载失败: ' + data.message);
            }
        } catch (e) {
            console.error(e);
        }
    }

    function renderProfile() {
        document.getElementById('nav-username').innerText = currentUser.name || currentUser.nickname || currentUser.phone;

        document.getElementById('val-name').innerText = currentUser.name || '-';
        document.getElementById('val-phone').innerText = currentUser.phone || '-';
        document.getElementById('val-email').innerText = currentUser.email || '-';
        document.getElementById('val-position').innerText = currentUser.targetPosition || '-';

        document.getElementById('in-name').value = currentUser.name || '';
        document.getElementById('in-phone').value = currentUser.phone || '';
        document.getElementById('in-email').value = currentUser.email || '';
        document.getElementById('in-position').value = currentUser.targetPosition || '';
    }

    function toggleEdit() {
        document.getElementById('profile-card').classList.toggle('editing');
    }

    async function saveProfile() {
        const updates = {
            name: document.getElementById('in-name').value,
            email: document.getElementById('in-email').value,
            targetPosition: document.getElementById('in-position').value
        };

        try {
            const res = await fetch('api/profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(updates)
            });
            const data = await res.json();
            if (data.success) {
                currentUser = data.user; // Update local
                renderProfile();
                toggleEdit();
                alert('保存成功');
            } else {
                alert('保存失败: ' + data.message);
            }
        } catch (e) {
            alert('网络错误');
        }
    }

    async function deleteAccount() {
        if (!confirm('确定要注销账号吗？该操作不可恢复！')) return;

        try {
            const res = await fetch('api/profile', {
                method: 'DELETE'
            });
            const data = await res.json();
            if (data.success) {
                alert('账号已注销');
                location.href = 'login.jsp';
            } else {
                alert('注销失败: ' + data.message);
            }
        } catch (e) {
            // Fallback for environments that might block DELETE
            try {
                 const res = await fetch('api/profile', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({action: 'delete'})
                });
                const data = await res.json();
                if (data.success) {
                    alert('账号已注销');
                    location.href = 'login.jsp';
                }
            } catch (ignore) {
                 alert('网络错误');
            }
        }
    }

    // Load on start
    loadProfile();
</script>
</body>
</html>

